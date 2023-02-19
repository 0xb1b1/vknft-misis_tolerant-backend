#!/usr/bin/env python3

from fastapi import FastAPI, Body, Depends, Header

from modules.auth.model import (
    UserLoginSchema,
    UserSimpleLoginSchema,
    EventCreateSchema,
    EventResponseSchema,
    TicketCreateSchema,
    TicketResponseSchema,
)
from modules.auth.handler import signJWT
from modules.auth.bearer import JWTBearer

import logging  # Logging important events
from dotenv import load_dotenv  # Load environment variables from .env
from os import getenv  # Get environment variables
from modules.db import DBManager  # Database manager
from modules import contracts  # Smart contracts
from modules.auth.state import AuthPair
from modules.imagetools import ImageTools
from modules.nftimage.nftimage import NFTImage


# region Logging
# Create a logger instance
log = logging.getLogger("backend")
# Create log formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Сreate console logging handler and set its level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# region Docker check
# Check if we are under Docker
DOCKER_MODE = getenv("DOCKER_MODE")
if getenv("DOCKER_MODE") == "true":
    DOCKER_MODE = True
    log.warning("Docker mode enabled")
else:
    log.warning("Docker mode disabled")

# Load environment variables from .env file
if not DOCKER_MODE:
    load_dotenv()
# endregion

# Create file logging handler and set its level
if DOCKER_MODE:
    logfile_path = r"/data/backend.log"
else:
    logfile_path = r"backend.log"
fh = logging.FileHandler(logfile_path)
fh.setFormatter(formatter)
log.addHandler(fh)

# Set logging level
logging_level_lower = getenv("LOGGING_LEVEL").lower()
if logging_level_lower == "debug":
    log.setLevel(logging.DEBUG)
    log.critical("Log level set to debug")
elif logging_level_lower == "info":
    log.setLevel(logging.INFO)
    log.critical("Log level set to info")
elif logging_level_lower == "warning":
    log.setLevel(logging.WARNING)
    log.critical("Log level set to warning")
elif logging_level_lower == "error":
    log.setLevel(logging.ERROR)
    log.critical("Log level set to error")
elif logging_level_lower == "critical":
    log.setLevel(logging.CRITICAL)
    log.critical("Log level set to critical")
# endregion

# region DB
db = DBManager(log)
# endregion

# region API
# Create FastAPI instance
api = FastAPI()

# region Auth state store
authpair = AuthPair()
# endregion

# region Images
nftimage = NFTImage()
image_tool = ImageTools(getenv("PICTSHARE_URL"))
# endregion

# region Helper functions
def check_user(data: UserLoginSchema) -> bool:
    """Log in via VK ID"""
    if db.auth(data.vk_id, data.wallet_public_key):
        return True
    else:
        return False


def get_token(token: str) -> str:
    """Get token without Bearer"""
    return token.split(" ")[1]


# endregion

# region Endpoints
@api.get("/", tags=["root"])
async def root():
    return {"message": "I love NFTs!"}


@api.post("/auth/login", tags=["auth"])
async def login(user: UserLoginSchema = Body(...)):
    db.auth(user.vk_id, user.wallet_public_key, user.first_name, user.last_name)
    token = signJWT(user.vk_id)
    # Store the token in authpair
    authpair.post(token["access_token"], user.vk_id)
    return token


@api.post("/auth/nwlogin", tags=["auth"])
async def nowallet_login(user: UserSimpleLoginSchema = Body(...)):
    if not db.auth(user.vk_id, None, None, None):
        return {"message": "User not found"}
    token = signJWT(user.vk_id)
    # Store the token in authpair
    authpair.post(token["access_token"], user.vk_id)
    return token


# region Protected
@api.get("/get/nfts", dependencies=[Depends(JWTBearer())], tags=["user", "nft"])
async def get_nfts(authorization: str = Header(None)):
    token = get_token(authorization)
    wallet_addr = db.get_user_wallet(authpair.get(token))
    return await contracts.get_all_nfts(wallet_addr)


@api.post("/create/event", dependencies=[Depends(JWTBearer())], tags=["event", "admin"])
async def create_event(event: EventCreateSchema, authorization: str = Header(None)):
    token = get_token(authorization)
    user_id = authpair.get(token)
    result = await contracts.create_collection(
        event.title,
        event.description,
        "https://moslenta.ru/thumb/1200x0/filters:quality(75):no_upscale()/imgs/2022/06/18/08/5455737/74cfc9ad503e4e49396f70bef990387c5b796d9b.jpg",  # image_tool.upload(event.image)
    )
    log.warning(result)
    collection_id = str(result["id"])

    # wallet_addr = db.get_user_wallet(authpair.get(token))
    # wallet_addr = db.get_user_wallet(authpair.get(token))
    # image_url = event.image#image.upload(event.image)
    # result = await contracts.create_collection(
    #     event.title, event.description, image_url
    # )
    # if "error" in result:
    #     return result
    # Write event to DB
    #! What do we have in result?

    db_event = db.create_event(event, user_id, collection_id)

    return {"eventId": db_event.id}  # EventResponseSchema.from_orm(db_event)


@api.post(
    "/create/ticket", dependencies=[Depends(JWTBearer())], tags=["event", "admin"]
)
async def create_nft(ticket: TicketCreateSchema, authorization: str = Header(None)):
    token = get_token(authorization)

    tk = db.create_nft(ticket)

    return TicketResponseSchema.from_orm(tk)  # EventResponseSchema.from_orm(db_event)


@api.get("/get/events", dependencies=[Depends(JWTBearer())], tags=["event"])
async def get_events():
    return db.get_events()


@api.get(
    "/get/event/nfts",
    dependencies=[Depends(JWTBearer())],
    tags=["event"],
    response_model=list[TicketResponseSchema],
)
async def get_events(event_id: int):
    return db.get_nfts(event_id)


@api.get("/get/event/allowlist", dependencies=[Depends(JWTBearer())], tags=["event"])
async def get_event_allowlist(event_id: int):
    return {"event_id": event_id, "allowlist": db.get_event_allowlist(event_id)}


@api.get("/get/users", dependencies=[Depends(JWTBearer())], tags=["user"])
async def get_users():
    return db.get_users()


# endregion
# endregion

# region Tests
@api.get("/test/get_users", tags=["tests"])
async def get_users_test():
    return db.get_users_test()


# endregion
# endregion
