"""
Custom exception classes for unified error handling
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, code: str = "APP_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(AppException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", error_details)
        self.field = field


class NotFoundError(AppException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "NOT_FOUND", {"resource": resource, "identifier": identifier})
        self.resource = resource
        self.identifier = identifier


class PathTraversalError(AppException):
    """Raised when path traversal attempt is detected"""

    def __init__(self, path: str):
        super().__init__(
            f"Path traversal detected: {path}",
            "PATH_TRAVERSAL",
            {"path": path}
        )
        self.path = path


class PluginNotFoundError(AppException):
    """Raised when requested ASR plugin is not available"""

    def __init__(self, plugin_name: str, available_plugins: Optional[list] = None):
        message = f"Plugin not found: {plugin_name}"
        if available_plugins:
            message += f". Available: {', '.join(available_plugins)}"
        super().__init__(message, "PLUGIN_NOT_FOUND", {"plugin": plugin_name, "available": available_plugins})
        self.plugin_name = plugin_name


class ProcessingError(AppException):
    """Raised when media processing fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "PROCESSING_ERROR", details)
