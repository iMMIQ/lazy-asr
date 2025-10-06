import os
import uuid
import zipfile
import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List
import json
from app.services.asr_service import ASRService
from plugins.manager import plugin_manager
from app.models.schemas import ASRResponse, MultiFileASRResponse, FileResult
from app.core.config import settings

router = APIRouter()
asr_service = ASRService()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ASR Service is running"}


@router.get("/plugins")
async def get_available_plugins():
    """Get list of available ASR plugins"""
    plugins = plugin_manager.get_available_plugins()
    return {"plugins": plugins}


@router.post("/process", response_model=ASRResponse)
async def process_audio(
    audio_file: UploadFile = File(...),
    asr_method: str = Form(settings.DEFAULT_ASR_METHOD),
    vad_options: Optional[str] = Form(None),
    asr_options: Optional[str] = Form(None),
    min_speech_duration: Optional[int] = Form(None),
    min_silence_duration: Optional[int] = Form(None),
    asr_api_url: Optional[str] = Form(None),
    asr_api_key: Optional[str] = Form(None),
    asr_model: Optional[str] = Form(None),
    language: Optional[str] = Form("auto"),  # Default to auto detect
    output_formats: Optional[str] = Form("srt"),  # Default to srt for backward compatibility
):
    """
    Process audio file through ASR pipeline

    Args:
        audio_file: Audio file to process
        asr_method: ASR method to use
        vad_options: VAD options as JSON string
        asr_options: ASR options as JSON string
        min_speech_duration: Minimum speech duration in milliseconds
        min_silence_duration: Minimum silence duration in milliseconds
    """
    try:
        # Validate ASR method
        available_plugins = plugin_manager.get_available_plugins()
        if asr_method not in available_plugins:
            raise HTTPException(
                status_code=400, detail=f"Unsupported ASR method: {asr_method}. Available methods: {available_plugins}"
            )

        # Parse options
        parsed_vad_options = None
        if vad_options:
            try:
                parsed_vad_options = json.loads(vad_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid VAD options JSON")

        parsed_asr_options = None
        if asr_options:
            try:
                parsed_asr_options = json.loads(asr_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid ASR options JSON")

        # Handle individual VAD parameters
        if min_speech_duration is not None or min_silence_duration is not None:
            if parsed_vad_options is None:
                parsed_vad_options = {}
            if min_speech_duration is not None:
                parsed_vad_options['min_speech_duration_ms'] = min_speech_duration
            if min_silence_duration is not None:
                parsed_vad_options['min_silence_duration_ms'] = min_silence_duration

        # Save uploaded file
        task_id = str(uuid.uuid4())
        upload_dir = os.path.join(settings.UPLOAD_DIR, task_id)
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, audio_file.filename)
        with open(file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)

        # Parse output formats
        parsed_output_formats = None
        if output_formats:
            # Support comma-separated formats: "srt,vtt,lrc" or single format: "srt"
            parsed_output_formats = [fmt.strip() for fmt in output_formats.split(',')]

        # Process audio
        result = await asr_service.process_audio(
            audio_path=file_path,
            asr_method=asr_method,
            vad_options=parsed_vad_options,
            asr_options=parsed_asr_options,
            asr_api_url=asr_api_url,
            asr_api_key=asr_api_key,
            asr_model=asr_model,
            language=language,
            output_formats=parsed_output_formats,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/process-multiple", response_model=MultiFileASRResponse)
async def process_multiple_audio(
    audio_files: List[UploadFile] = File(...),
    asr_method: str = Form(settings.DEFAULT_ASR_METHOD),
    vad_options: Optional[str] = Form(None),
    asr_options: Optional[str] = Form(None),
    min_speech_duration: Optional[int] = Form(None),
    min_silence_duration: Optional[int] = Form(None),
    asr_api_url: Optional[str] = Form(None),
    asr_api_key: Optional[str] = Form(None),
    asr_model: Optional[str] = Form(None),
    language: Optional[str] = Form("auto"),  # Default to auto detect
    output_formats: Optional[str] = Form("srt"),
):
    """
    Process multiple audio files through ASR pipeline

    Args:
        audio_files: List of audio files to process
        asr_method: ASR method to use
        vad_options: VAD options as JSON string
        asr_options: ASR options as JSON string
        min_speech_duration: Minimum speech duration in milliseconds
        min_silence_duration: Minimum silence duration in milliseconds
    """
    try:
        # Validate ASR method
        available_plugins = plugin_manager.get_available_plugins()
        if asr_method not in available_plugins:
            raise HTTPException(
                status_code=400, detail=f"Unsupported ASR method: {asr_method}. Available methods: {available_plugins}"
            )

        # Validate files
        if not audio_files:
            raise HTTPException(status_code=400, detail="No audio files provided")

        if len(audio_files) > 10:  # Limit to 10 files per batch
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files per batch")

        # Parse options
        parsed_vad_options = None
        if vad_options:
            try:
                parsed_vad_options = json.loads(vad_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid VAD options JSON")

        parsed_asr_options = None
        if asr_options:
            try:
                parsed_asr_options = json.loads(asr_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid ASR options JSON")

        # Handle individual VAD parameters
        if min_speech_duration is not None or min_silence_duration is not None:
            if parsed_vad_options is None:
                parsed_vad_options = {}
            if min_speech_duration is not None:
                parsed_vad_options['min_speech_duration_ms'] = min_speech_duration
            if min_silence_duration is not None:
                parsed_vad_options['min_silence_duration_ms'] = min_silence_duration

        # Parse output formats
        parsed_output_formats = None
        if output_formats:
            parsed_output_formats = [fmt.strip() for fmt in output_formats.split(',')]

        # Process all files
        batch_id = str(uuid.uuid4())
        file_results = []
        processed_files = 0
        failed_files = 0

        for audio_file in audio_files:
            try:
                # Save uploaded file
                task_id = str(uuid.uuid4())
                upload_dir = os.path.join(settings.UPLOAD_DIR, task_id)
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, audio_file.filename)
                with open(file_path, "wb") as buffer:
                    content = await audio_file.read()
                    buffer.write(content)

                # Process audio
                result = await asr_service.process_audio(
                    audio_path=file_path,
                    asr_method=asr_method,
                    vad_options=parsed_vad_options,
                    asr_options=parsed_asr_options,
                    asr_api_url=asr_api_url,
                    asr_api_key=asr_api_key,
                    asr_model=asr_model,
                    language=language,
                    output_formats=parsed_output_formats,
                )

                # Convert to FileResult
                file_result = FileResult(
                    filename=audio_file.filename,
                    success=result.success,
                    message=result.message,
                    output_files=result.output_files,
                    segments=result.segments,
                    stats=result.stats,
                    failed_segments_details=result.failed_segments_details,
                    task_id=result.task_id,
                )
                file_results.append(file_result)
                processed_files += 1

            except Exception as e:
                # Create failed result for this file
                file_result = FileResult(
                    filename=audio_file.filename,
                    success=False,
                    message=f"Processing failed: {str(e)}",
                    output_files=None,
                    segments=None,
                    stats=None,
                    failed_segments_details=None,
                    task_id=None,
                )
                file_results.append(file_result)
                failed_files += 1

        # Calculate overall stats
        total_subtitles = sum(
            result.stats.get('total_subtitles', 0) for result in file_results if result.success and result.stats
        )
        total_segments = sum(
            result.stats.get('total_segments', 0) for result in file_results if result.success and result.stats
        )

        overall_stats = {
            "total_files": len(audio_files),
            "successful_files": processed_files,
            "failed_files": failed_files,
            "total_subtitles": total_subtitles,
            "total_segments": total_segments,
        }

        success = processed_files > 0  # Consider batch successful if at least one file succeeded

        return MultiFileASRResponse(
            success=success,
            message=f"Batch processing completed. {processed_files} files processed, {failed_files} files failed.",
            batch_id=batch_id,
            total_files=len(audio_files),
            processed_files=processed_files,
            failed_files=failed_files,
            file_results=file_results,
            overall_stats=overall_stats,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download generated SRT file"""
    # Security check - ensure file is within output directory
    full_path = os.path.abspath(file_path)
    output_dir = os.path.abspath(settings.OUTPUT_DIR)

    if not full_path.startswith(output_dir):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, media_type='application/octet-stream')


@router.get("/download-bundle/{task_id}")
async def download_bundle(task_id: str):
    """
    Download all subtitle files for a task as a ZIP bundle

    Args:
        task_id: The task ID to download files for
    """
    try:
        # Security check - ensure task_id is valid
        task_output_dir = os.path.join(settings.OUTPUT_DIR, task_id)
        if not os.path.exists(task_output_dir):
            raise HTTPException(status_code=404, detail="Task not found")

        # Find all subtitle files in the task directory
        subtitle_files = []
        for root, dirs, files in os.walk(task_output_dir):
            for file in files:
                if file.endswith(('.srt', '.vtt', '.lrc', '.txt')):
                    subtitle_files.append(os.path.join(root, file))

        if not subtitle_files:
            raise HTTPException(status_code=404, detail="No subtitle files found for this task")

        # Create ZIP file in memory with proper Unicode filename handling
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, subtitle_file in enumerate(subtitle_files):
                # Read file content
                with open(subtitle_file, 'rb') as f:
                    file_content = f.read()

                # Use simple numeric filenames to avoid encoding issues
                file_extension = os.path.splitext(subtitle_file)[1]
                safe_filename = f"subtitle_{i+1}{file_extension}"

                # Add file to ZIP
                zip_file.writestr(safe_filename, file_content)

        zip_buffer.seek(0)

        # Get base filename for ZIP file naming - use ASCII-only name
        zip_filename = f"subtitles_bundle_{task_id}.zip"

        # Return ZIP file as response using StreamingResponse
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename="{zip_filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bundle: {str(e)}")
