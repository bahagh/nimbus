from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    email: str = Field(examples=["demo@example.com"])
    password: str = Field(examples=["demo123"])

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
