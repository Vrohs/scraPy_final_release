from typing import Any, Dict, Optional

class ScrapyBaseException(Exception):
    """Base exception for all ScraPy errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ResourceNotFoundException(ScrapyBaseException):
    def __init__(self, resource: str, id: Any):
        super().__init__(
            message=f"{resource} with id {id} not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": id}
        )

class ValidationException(ScrapyBaseException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )

class AuthenticationException(ScrapyBaseException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )

class PermissionDeniedException(ScrapyBaseException):
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403
        )

class ScrapingException(ScrapyBaseException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SCRAPING_ERROR",
            status_code=502,
            details=details
        )
