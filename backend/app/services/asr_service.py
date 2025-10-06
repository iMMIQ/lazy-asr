import os
import uuid
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logger import get_logger
from app.utils.audio_processing import (
    silero_vad_segmentation,
    export_silero_segments,
    parse_transcription_segments,
    time_string_to_seconds,
)
from app.utils.subtitle_formatters import generate_subtitle_files
from plugins.manager import plugin_manager
from app.models.schemas import ASRResponse

logger = get_logger(__name__)


class ASRService:
    """Main ASR service that orchestrates the entire process"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    async def process_audio(
        self,
        audio_path: str,
        asr_method: str = "faster-whisper",
        vad_options: Optional[Dict[str, Any]] = None,
        asr_options: Optional[Dict[str, Any]] = None,
        asr_api_url: Optional[str] = None,
        asr_api_key: Optional[str] = None,
        asr_model: Optional[str] = None,
        output_formats: List[str] = None,
    ) -> ASRResponse:
        """
        Process audio file through the complete ASR pipeline

        Args:
            audio_path: Path to the audio file
            asr_method: ASR method to use
            vad_options: VAD options
            asr_options: ASR options

        Returns:
            ASRResponse with results
        """
        try:
            logger.info("Starting Silero VAD automatic segmentation transcription process")
            logger.info("=" * 60)
            logger.info(f"ASR method: {asr_method}")
            logger.info(f"Output directory: {self.output_dir}")

            # Check if file exists
            if not os.path.exists(audio_path):
                logger.error(f"Audio file does not exist: {audio_path}")
                return ASRResponse(success=False, message="Audio file does not exist")

            # Create task ID and output directory
            task_id = str(uuid.uuid4())
            task_output_dir = os.path.join(self.output_dir, task_id)
            os.makedirs(task_output_dir, exist_ok=True)

            # 1. Silero VAD segmentation
            try:
                speech_timestamps, audio_data, sample_rate = silero_vad_segmentation(audio_path, vad_options or {})
            except Exception as e:
                logger.error(f"Silero VAD detection failed: {e}")
                return ASRResponse(success=False, message=f"Silero VAD detection failed: {e}")

            if not speech_timestamps:
                logger.error("No speech segments detected")
                return ASRResponse(success=False, message="No speech segments detected")

            # 2. Export segment audio
            logger.info("Exporting speech segment files...")
            segments_output_dir = os.path.join(task_output_dir, "silero_segments")
            exported_segments = export_silero_segments(speech_timestamps, audio_data, sample_rate, segments_output_dir)

            if not exported_segments:
                logger.error("No speech segments available for export")
                return ASRResponse(success=False, message="No speech segments available for export")

            # 3. Get ASR plugin
            plugin = plugin_manager.get_plugin(asr_method)
            if not plugin:
                logger.error(f"Unsupported ASR method: {asr_method}")
                return ASRResponse(success=False, message=f"Unsupported ASR method: {asr_method}")

            # Update plugin configuration
            plugin_config = {}
            if asr_api_url:
                plugin_config['api_url'] = asr_api_url
            if asr_api_key:
                plugin_config['api_key'] = asr_api_key
            if asr_model:
                plugin_config['model'] = asr_model

            if plugin_config:
                plugin.update_config(plugin_config)
                logger.info(f"Updated plugin configuration: {plugin_config}")

            # 4. Concurrent transcription
            logger.info("Starting concurrent transcription...")
            all_subtitles = []
            successful_transcriptions = 0
            failed_segments = 0
            empty_segments = 0
            failed_segments_details = []

            # Use plugin to transcribe all segments concurrently
            transcription_results = await plugin.transcribe_segments(exported_segments)

            for i, result in enumerate(transcription_results):
                # Use segment_info from result to get correct segment information
                segment_info = result.get('segment_info')
                if not segment_info:
                    # If result doesn't have segment_info, use index to find it
                    segment_index = result.get('segment_index', i)
                    if segment_index < len(exported_segments):
                        segment_info = exported_segments[segment_index]
                    else:
                        logger.error(f"Cannot find corresponding segment information, index: {segment_index}")
                        failed_segments += 1
                        continue
                
                logger.info(f"[{i+1}/{len(exported_segments)}] Processing speech segment:")
                logger.info(f"  File: {os.path.basename(segment_info['file_path'])}")
                logger.info(f"  Time: {segment_info['start_time']:.2f}s - {segment_info['end_time']:.2f}s")
                logger.info(f"  Duration: {segment_info['duration']:.2f}s")

                if not result['success']:
                    # Transcription failed, record detailed information
                    error_msg = result['error'] or "Unknown error"
                    error_type = result['error_type'] or "UnknownError"
                    logger.error(f"  Transcription failed: {error_msg} (type: {error_type})")
                    failed_segments += 1

                    # Record failed segment details
                    failed_segment_detail = {
                        'index': segment_info['index'],
                        'start_time': segment_info['start_time'],
                        'end_time': segment_info['end_time'],
                        'duration': segment_info['duration'],
                        'file_path': segment_info['file_path'],
                        'error': error_msg,
                        'error_type': error_type,
                    }
                    failed_segments_details.append(failed_segment_detail)
                    continue

                transcription = result['transcription']
                if transcription is None:
                    # No transcription content, skip this segment
                    logger.warning(f"  No transcription content, skipping segment")
                    empty_segments += 1
                    continue

                # Parse transcription results
                adjusted_subtitles = parse_transcription_segments(
                    transcription, segment_info['start_time'], segment_info['end_time']
                )

                if adjusted_subtitles:
                    all_subtitles.extend(adjusted_subtitles)
                    successful_transcriptions += 1
                    logger.info(f"  Successfully added {len(adjusted_subtitles)} subtitles")

                    # Show first subtitle preview
                    if adjusted_subtitles:
                        first_sub = adjusted_subtitles[0]
                        preview_text = (
                            first_sub['text'][:50] + "..." if len(first_sub['text']) > 50 else first_sub['text']
                        )
                        logger.info(f"  Preview: {preview_text}")
                else:
                    logger.warning(f"  No transcription content, skipping segment")
                    empty_segments += 1

            # 5. Generate subtitle files
            if all_subtitles:
                # Sort subtitles by time
                all_subtitles.sort(key=lambda x: time_string_to_seconds(x['start'].replace(',', '.')))

                # Set default output formats
                if output_formats is None:
                    output_formats = ['srt']

                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                base_output_path = os.path.join(task_output_dir, f"{base_name}_silero_subtitles")

                # Generate multiple format subtitle files
                output_files = generate_subtitle_files(all_subtitles, base_output_path, output_formats)

                # Generate statistics
                stats = {
                    "total_segments": len(exported_segments),
                    "successful_transcriptions": successful_transcriptions,
                    "failed_segments": failed_segments,
                    "empty_segments": empty_segments,
                    "total_subtitles": len(all_subtitles),
                    "output_formats": output_formats,
                }

                logger.info("Processing completed!")
                logger.info("Statistics:")
                logger.info(f"  Total speech segments: {len(exported_segments)}")
                logger.info(f"  Successful transcriptions: {successful_transcriptions}")
                logger.info(f"  Failed segments: {failed_segments}")
                logger.info(f"  Empty segments: {empty_segments}")
                logger.info(f"  Total subtitles: {len(all_subtitles)}")
                logger.info(f"  Output formats: {', '.join(output_formats)}")

                # Display generated files
                for fmt, file_path in output_files.items():
                    logger.info(f"  {fmt.upper()} file saved: {file_path}")

                # Display failed segment details
                if failed_segments_details:
                    logger.info("Failed segment details:")
                    logger.info("=" * 60)
                    for failed_segment in failed_segments_details:
                        logger.info(f"  Segment {failed_segment['index']+1}:")
                        logger.info(f"    Time: {failed_segment['start_time']:.2f}s - {failed_segment['end_time']:.2f}s")
                        logger.info(f"    Duration: {failed_segment['duration']:.2f}s")
                        logger.info(f"    Error type: {failed_segment['error_type']}")
                        logger.info(f"    Error message: {failed_segment['error']}")
                        logger.info(f"    File: {os.path.basename(failed_segment['file_path'])}")
                        logger.info("")

                # Preview first few subtitles
                preview_text = "Subtitle preview:\n" + "=" * 50 + "\n"
                for i, subtitle in enumerate(all_subtitles[:5]):
                    preview_text += f"{i+1}\n"
                    preview_text += f"{subtitle['start']} --> {subtitle['end']}\n"
                    preview_text += f"{subtitle['text']}\n\n"

                # Backward compatibility: keep srt_file_path field
                srt_file_path = output_files.get('srt')

                return ASRResponse(
                    success=True,
                    message=f"Processing completed! Generated {len(output_files)} format subtitle files",
                    srt_file_path=srt_file_path,  # Backward compatibility
                    output_files=output_files,  # New field: all format file paths
                    segments=[s for s in all_subtitles[:10]],  # Return only first 10 subtitles
                    stats=stats,
                    failed_segments_details=failed_segments_details,
                    task_id=task_id,  # Add task ID for bundle download
                )
            else:
                error_msg = "No subtitles generated"
                logger.error(error_msg)

                # Display failed segment details
                if failed_segments_details:
                    logger.info("Failed segment details:")
                    logger.info("=" * 60)
                    for failed_segment in failed_segments_details:
                        logger.info(f"  Segment {failed_segment['index']+1}:")
                        logger.info(f"    Time: {failed_segment['start_time']:.2f}s - {failed_segment['end_time']:.2f}s")
                        logger.info(f"    Duration: {failed_segment['duration']:.2f}s")
                        logger.info(f"    Error type: {failed_segment['error_type']}")
                        logger.info(f"    Error message: {failed_segment['error']}")
                        logger.info(f"    File: {os.path.basename(failed_segment['file_path'])}")
                        logger.info("")

                return ASRResponse(success=False, message=error_msg, failed_segments_details=failed_segments_details)

        except Exception as e:
            logger.error(f"Error occurred during processing: {e}")
            return ASRResponse(success=False, message=f"Error occurred during processing: {e}")
