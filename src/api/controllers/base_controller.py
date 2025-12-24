from typing import Any, Callable, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)

class BaseController:
    """
    Base Controller class to standardize API responses and error handling.
    """

    @staticmethod
    def success_response(data: Any, message: str = "Success", status_code: int = status.HTTP_200_OK) -> Dict[str, Any]:
        """
        Standardized success response format.
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "code": status_code
        }

    @staticmethod
    def error_response(message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[Any] = None) -> JSONResponse:
        """
        Standardized error response format for returning JSONResponses directly.
        """
        content = {
            "status": "error",
            "message": message,
            "code": status_code
        }
        if details:
            content["details"] = details
            
        return JSONResponse(
            status_code=status_code,
            content=content
        )

    @classmethod
    def safe_execute(cls, func: Callable, *args, **kwargs) -> Any:
        """
        Wrapper to execute service/repository calls with centralized try-catch and logging.
        Returns the result of the function or raises an HTTPException.
        """
        try:
            return func(*args, **kwargs)
        except HTTPException as http_ex:
            # Re-raise HTTP exceptions as they are already handled
            logger.warning(f"HTTPException in {func.__name__}: {http_ex.detail}")
            raise http_ex
        except ValueError as ve:
            # Handle bad request errors usually raised as ValueErrors
            logger.error(f"ValueError in {func.__name__}: {str(ve)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="An internal server error occurred."
            )
