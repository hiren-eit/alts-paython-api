from pydantic import BaseModel, Field

class TokenRequest(BaseModel):
    clientId: str = Field(..., description="The client ID for authentication")
    clientSecret: str = Field(..., description="The client secret for authentication")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
