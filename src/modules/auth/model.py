from pydantic import BaseModel, Field, EmailStr


class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens...."
            }
        }

class UserSchema(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    vk_id: int = Field(...)
    wallet_public_key: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Alandez",
                "last_name": "Abdulazeez",
                "vk_id": "123456789",
                "wallet_public_key": "ABCDE123456789",
            }
        }

class UserLoginSchema(BaseModel):
    vk_id: int = Field(...)
    wallet_public_key: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "vk_id": "123456789",
                "wallet_public_key": "ABCDE123456789",
            }
        }