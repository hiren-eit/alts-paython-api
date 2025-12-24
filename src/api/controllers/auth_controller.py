from fastapi import status, HTTPException
from src.api.controllers.base_controller import BaseController
from src.domain.dtos.auth_dto import TokenRequest, TokenResponse
from src.core.security import create_access_token
from src.core.settings import settings

class AuthController(BaseController):
    """
    Controller for handling authentication logic.
    """

    @classmethod
    def login(cls, request: TokenRequest) -> TokenResponse:
        """
        Validate client credentials and return a token.
        """
        # Dummy validation as requested
        if request.clientId == settings.client_id and request.clientSecret == settings.client_secret:
            access_token = create_access_token(data={"sub": request.clientId})
            return TokenResponse(
                access_token=access_token,
                expires_in=settings.access_token_expire_minutes * 60
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client ID or client secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
