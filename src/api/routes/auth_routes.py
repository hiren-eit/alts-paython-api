from typing import Optional
from fastapi import APIRouter, Body, Request, HTTPException, status
import base64

from src.api.controllers.auth_controller import AuthController
from src.domain.dtos.auth_dto import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
async def login(
    request: Request,
    body: Optional[TokenRequest] = Body(None),
):
    """
    Issues JWT token using clientId and clientSecret.

    Supported input:
    - JSON body
    - Basic Auth header
    - Form-urlencoded (Swagger compatibility)
    """

    # 1. JSON body (preferred)
    if body and body.clientId and body.clientSecret:
        return AuthController.login(body)

    content_type = request.headers.get("content-type", "")

    # 2. Basic Auth header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Basic "):
        try:
            encoded = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            client_id, client_secret = decoded.split(":", 1)

            return AuthController.login(
                TokenRequest(
                    clientId=client_id,
                    clientSecret=client_secret
                )
            )
        except Exception:
            pass

    # 3. Form data (Swagger sends this)
    if "application/x-www-form-urlencoded" in content_type:
        try:
            form = await request.form()
            client_id = form.get("client_id")
            client_secret = form.get("client_secret")

            if client_id and client_secret:
                return AuthController.login(
                    TokenRequest(
                        clientId=client_id,
                        clientSecret=client_secret
                    )
                )
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="clientId and clientSecret are required",
    )
