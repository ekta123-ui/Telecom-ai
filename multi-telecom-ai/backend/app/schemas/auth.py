from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    mobile_number: str = Field(pattern=r"^[6-9]\d{9}$")
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: str
    mobile_number: str
    role: str

    model_config = ConfigDict(from_attributes=True)