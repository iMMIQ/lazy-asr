import os
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings
from app.utils.audio_processing import (
    silero_vad_segmentation, 
    export_silero_segments,
    parse_transcription_segments,
    time_string_to_seconds,
    generate_srt_content
)
from plugins.manager import plugin_manager
from app.models.schemas import ASRResponse
from app.api.websocket import ProgressPublisher


class ASRService:
    """Main ASR service that orchestrates the entire process"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def process_audio(self, audio_path: str, asr_method: str = "faster-whisper",
                           vad_options: Optional[Dict[str, Any]] = None,
                           asr_options: Optional[Dict[str, Any]] = None,
                           asr_api_url: Optional[str] = None,
                           asr_api_key: Optional[str] = None,
                           asr_model: Optional[str] = None,
                           task_id: Optional[str] = None) -> ASRResponse:
        """
        Process audio file through the complete ASR pipeline with real-time progress updates
        
        Args:
            audio_path: Path to the audio file
            asr_method: ASR method to use
            vad_options: VAD options
            asr_options: ASR options
            task_id: Task ID for WebSocket communication
            
        Returns:
            ASRResponse with results
        """
        # Create task ID if not provided
        if not task_id:
            task_id = str(uuid.uuid4())
        
        # Create progress publisher for WebSocket updates
        progress_publisher = ProgressPublisher(task_id)
        
        try:
            # Send initial progress update
            await progress_publisher.send_progress(
                step="initialization",
                message="🚀 Starting Silero VAD automatic segmentation transcription process",
                progress=0.0
            )
            
            await progress_publisher.send_log("info", f"ASR Method: {asr_method}")
            await progress_publisher.send_log("info", f"Output Directory: {self.output_dir}")
            
            # Check if file exists
            if not os.path.exists(audio_path):
                error_msg = f"❌ Audio file does not exist: {audio_path}"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
            
            # Create task output directory
            task_output_dir = os.path.join(self.output_dir, task_id)
            os.makedirs(task_output_dir, exist_ok=True)
            
            # 1. Silero VAD speech segmentation
            await progress_publisher.send_progress(
                step="vad_detection",
                message="🔍 Performing Silero VAD speech detection and segmentation",
                progress=10.0
            )
            
            try:
                speech_timestamps, audio_data, sample_rate = silero_vad_segmentation(
                    audio_path, vad_options or {}
                )
                await progress_publisher.send_log("info", f"VAD detected {len(speech_timestamps)} speech segments")
            except Exception as e:
                error_msg = f"❌ Silero VAD detection failed: {e}"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
            
            if not speech_timestamps:
                error_msg = "❌ No speech segments detected"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
            
            # 2. Export segmented audio files
            await progress_publisher.send_progress(
                step="segment_export",
                message="📁 Exporting speech segment files",
                progress=30.0
            )
            
            segments_output_dir = os.path.join(task_output_dir, "silero_segments")
            exported_segments = export_silero_segments(
                speech_timestamps, audio_data, sample_rate, segments_output_dir
            )
            
            if not exported_segments:
                error_msg = "❌ No speech segments available for export"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
            
            await progress_publisher.send_log("info", f"Exported {len(exported_segments)} segment files")
            
            # 3. Get ASR plugin
            await progress_publisher.send_progress(
                step="plugin_setup",
                message="🔧 Setting up ASR plugin",
                progress=40.0
            )
            
            plugin = plugin_manager.get_plugin(asr_method)
            if not plugin:
                error_msg = f"❌ Unsupported ASR method: {asr_method}"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
            
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
                await progress_publisher.send_log("info", f"Updated plugin configuration: {plugin_config}")
            
            # 4. Concurrent transcription
            await progress_publisher.send_progress(
                step="transcription",
                message="🎯 Starting concurrent transcription of segments",
                progress=50.0
            )
            
            all_subtitles = []
            successful_transcriptions = 0
            failed_segments = 0
            empty_segments = 0
            
            # Use plugin to transcribe all segments concurrently
            transcription_results = await plugin.transcribe_segments(exported_segments)
            
            for i, result in enumerate(transcription_results):
                segment_info = exported_segments[i]
                segment_progress = 50.0 + (i / len(exported_segments)) * 40.0
                
                # Send segment processing update
                await progress_publisher.send_progress(
                    step="transcription",
                    message=f"Processing segment {i+1}/{len(exported_segments)}",
                    progress=segment_progress,
                    details={
                        "current_segment": i + 1,
                        "total_segments": len(exported_segments),
                        "segment_file": os.path.basename(segment_info['file_path']),
                        "segment_time": f"{segment_info['start_time']:.2f}s - {segment_info['end_time']:.2f}s",
                        "segment_duration": f"{segment_info['duration']:.2f}s"
                    }
                )
                
                if not result['success']:
                    # Transcription failed, skip this segment
                    await progress_publisher.send_log("error", f"Segment {i+1} transcription failed, skipping")
                    failed_segments += 1
                    continue
                
                transcription = result['transcription']
                if transcription is None:
                    # Transcription has no content, skip this segment
                    await progress_publisher.send_log("warning", f"Segment {i+1} has no transcription content, skipping")
                    empty_segments += 1
                    continue
                
                # Parse transcription results
                adjusted_subtitles = parse_transcription_segments(
                    transcription, 
                    segment_info['start_time'], 
                    segment_info['end_time']
                )
                
                if adjusted_subtitles:
                    all_subtitles.extend(adjusted_subtitles)
                    successful_transcriptions += 1
                    await progress_publisher.send_log("success", f"Segment {i+1} successfully added {len(adjusted_subtitles)} subtitles")
                    
                    # Show preview of first subtitle
                    if adjusted_subtitles:
                        first_sub = adjusted_subtitles[0]
                        preview_text = first_sub['text'][:50] + "..." if len(first_sub['text']) > 50 else first_sub['text']
                        await progress_publisher.send_log("info", f"Segment {i+1} preview: {preview_text}")
                else:
                    await progress_publisher.send_log("warning", f"Segment {i+1} has no transcription content, skipping")
                    empty_segments += 1
            
            # 5. Generate SRT file
            await progress_publisher.send_progress(
                step="srt_generation",
                message="💾 Generating SRT subtitle file",
                progress=95.0
            )
            
            if all_subtitles:
                # Sort subtitles by time
                all_subtitles.sort(key=lambda x: time_string_to_seconds(x['start'].replace(',', '.')))
                
                srt_content = generate_srt_content(all_subtitles)
                
                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                output_srt_path = os.path.join(task_output_dir, f"{base_name}_silero_subtitles.srt")
                
                with open(output_srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                
                # Generate statistics
                stats = {
                    "total_segments": len(exported_segments),
                    "successful_transcriptions": successful_transcriptions,
                    "failed_segments": failed_segments,
                    "empty_segments": empty_segments,
                    "total_subtitles": len(all_subtitles)
                }
                
                # Send completion message
                await progress_publisher.send_progress(
                    step="completion",
                    message="✅ Processing completed successfully!",
                    progress=100.0,
                    details=stats
                )
                
                await progress_publisher.send_log("success", f"SRT file saved: {output_srt_path}")
                await progress_publisher.send_log("info", f"Statistics: Total segments: {len(exported_segments)}, "
                                                       f"Successful: {successful_transcriptions}, "
                                                       f"Failed: {failed_segments}, "
                                                       f"Empty: {empty_segments}, "
                                                       f"Total subtitles: {len(all_subtitles)}")
                
                # Send completion result
                result_data = {
                    "success": True,
                    "message": f"✅ Processing completed! SRT file saved: {output_srt_path}",
                    "srt_file_path": output_srt_path,
                    "segments": [s for s in all_subtitles[:10]],  # Only return first 10 subtitles
                    "stats": stats
                }
                
                await progress_publisher.send_completion(result_data)
                
                return ASRResponse(
                    success=True,
                    message=f"✅ Processing completed! SRT file saved: {output_srt_path}",
                    srt_file_path=output_srt_path,
                    segments=[s for s in all_subtitles[:10]],
                    stats=stats
                )
            else:
                error_msg = "❌ No subtitles generated"
                await progress_publisher.send_error(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
                
        except Exception as e:
            error_msg = f"❌ Error occurred during processing: {e}"
            await progress_publisher.send_error(error_msg)
            return ASRResponse(
                success=False,
                message=error_msg
            )
