import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import json
from app.services.asr_service import ASRService
from plugins.manager import plugin_manager
from app.models.schemas import ASRResponse
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
    asr_model: Optional[str] = Form(None)
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
                status_code=400,
                detail=f"Unsupported ASR method: {asr_method}. Available methods: {available_plugins}"
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
        
        # Process audio
        result = await asr_service.process_audio(
            audio_path=file_path,
            asr_method=asr_method,
            vad_options=parsed_vad_options,
            asr_options=parsed_asr_options,
            asr_api_url=asr_api_url,
            asr_api_key=asr_api_key,
            asr_model=asr_model
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


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
