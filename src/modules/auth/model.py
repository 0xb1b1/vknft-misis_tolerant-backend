from typing import Set
from pydantic import BaseModel, Field, EmailStr, Json
from datetime import datetime


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


class TicketCreateSchema(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    image: bytes
    keys: dict[str, str]
    eventId: int

    class Config:
        schema_extra = {
            "example": {
                "name": "My NFT",
                "image": "https://i.ibb.co/28Wg0xd/pic-blur.png",
                "description": "An NFT commemorating a special day",
                "keys": ["vip", "regular"],
            }
        }


class TicketResponseSchema(BaseModel):
    id: int
    title: str = Field(...)
    description: str = Field(...)
    blurredImage: str
    # keys: dict[str, str]
    eventId: int
    blurredImage: str
    # mintHash: str
    # imageKey: str
    attended: bool

    class Config:
        orm_mode = True


class EventCreateSchema(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    place: str = Field(...)
    datetime: datetime  # unix time
    image: bytes = Field(...)  # bytes encoded PNG

    class Config:
        schema_extra = {
            "example": {
                "title": "Концерт “Максим”",
                "description": "В пятницу, 17 июня, певица МакSим дала первый после выхода из комы сольный популярный концерт.",
                "place": "Лужники",
                "datetime": 1676782161,
                "image": "https://moslenta.ru/thumb/1200x0/filters:quality(75):no_upscale()/imgs/2022/06/18/08/5455737/74cfc9ad503e4e49396f70bef990387c5b796d9b.jpg",
            }
        }


class EventResponseSchema(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    place: str = Field(...)
    datetime: datetime  # unix time
    ownerID: int
    collectionID: str
    tickets: list[int]

    class Config:
        orm_mode = True
