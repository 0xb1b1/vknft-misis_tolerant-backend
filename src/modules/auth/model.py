from pydantic import BaseModel, Field, EmailStr


class UserLoginSchema(BaseModel):
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

class UserSimpleLoginSchema(BaseModel):
    vk_id: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "vk_id": "123456789",
            }
        }
