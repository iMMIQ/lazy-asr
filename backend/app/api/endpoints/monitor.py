"""
Monitor management endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.monitor_service import monitor_service
from app.core.logger import get_logger

logger = get_logger(__name__)


# Monitor configuration models
class MonitorConfigCreate(BaseModel):
    name: str
    path: str
    recursive: bool = True
    asr_method: str = "local-whisper"
    output_formats: Optional[list[str]] = None
    auto_process: bool = True
    scan_interval: int = 3600


class MonitorConfigUpdate(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None
    is_active: Optional[bool] = None
    recursive: Optional[bool] = None
    asr_method: Optional[str] = None
    output_formats: Optional[list[str]] = None
    auto_process: Optional[bool] = None
    scan_interval: Optional[int] = None


router = APIRouter()


@router.post("/create")
async def create_monitor(config: MonitorConfigCreate):
    """
    Create a new monitor configuration

    Args:
        config: Monitor configuration
    """
    try:
        monitor = await monitor_service.create_monitor_config(
            name=config.name,
            path=config.path,
            recursive=config.recursive,
            asr_method=config.asr_method,
            output_formats=config.output_formats,
            auto_process=config.auto_process,
            scan_interval=config.scan_interval,
        )
        return {"message": "Monitor created successfully", "monitor": monitor.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create monitor: {str(e)}")


@router.get("/all")
async def get_all_monitors(active_only: bool = False):
    """
    Get all monitor configurations

    Args:
        active_only: If True, only return active monitors
    """
    try:
        monitors = await monitor_service.get_all_monitor_configs(active_only=active_only)
        return {"total_monitors": len(monitors), "monitors": [m.to_dict() for m in monitors]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitors: {str(e)}")


@router.get("/status")
async def get_monitor_service_status():
    """
    Get overall monitor service status
    """
    try:
        status = await monitor_service.get_monitor_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitor status: {str(e)}")


@router.post("/service/start")
async def start_monitor_service():
    """
    Start the monitor service
    """
    try:
        await monitor_service.start()
        return {"message": "Monitor service started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitor service: {str(e)}")


@router.post("/service/stop")
async def stop_monitor_service():
    """
    Stop the monitor service
    """
    try:
        await monitor_service.stop()
        return {"message": "Monitor service stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitor service: {str(e)}")


@router.get("/{monitor_id}")
async def get_monitor(monitor_id: int):
    """
    Get monitor configuration by ID

    Args:
        monitor_id: Monitor ID
    """
    try:
        monitor = await monitor_service.get_monitor_config(monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")
        return monitor.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitor: {str(e)}")


@router.put("/{monitor_id}")
async def update_monitor(monitor_id: int, config: MonitorConfigUpdate):
    """
    Update monitor configuration

    Args:
        monitor_id: Monitor ID to update
        config: Monitor configuration updates
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in config.model_dump().items() if v is not None}

        monitor = await monitor_service.update_monitor_config(monitor_id, **update_data)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        return {"message": "Monitor updated successfully", "monitor": monitor.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update monitor: {str(e)}")


@router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: int):
    """
    Delete monitor configuration

    Args:
        monitor_id: Monitor ID to delete
    """
    try:
        success = await monitor_service.delete_monitor_config(monitor_id)
        if not success:
            raise HTTPException(status_code=404, detail="Monitor not found")
        return {"message": "Monitor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete monitor: {str(e)}")


@router.post("/{monitor_id}/toggle")
async def toggle_monitor(monitor_id: int, is_active: bool = True):
    """
    Toggle monitor active status

    Args:
        monitor_id: Monitor ID to toggle
        is_active: Desired active status
    """
    try:
        monitor = await monitor_service.toggle_monitor_status(monitor_id, is_active=is_active)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        return {
            "message": f"Monitor {'activated' if is_active else 'deactivated'} successfully",
            "monitor": monitor.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle monitor: {str(e)}")
