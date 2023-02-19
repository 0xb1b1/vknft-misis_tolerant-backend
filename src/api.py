#!/usr/bin/env python3

from fastapi import FastAPI, Body, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import time
import json

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
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# region Auth state store
authpair = AuthPair()
# endregion

# region Images
nftimage = NFTImage()

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

# region BackgroundTask
def update_nft_status(data: tuple):
    internal_id = data[0]
    nft_id = data[1]
    collection_id = data[2]
    response = contracts.check_minting_status(nft_id, collection_id)
    log.info(response)
    log.info(f'hash: {response["onChain"]["status"]}')
    while response["onChain"]["status"] != "success":
        # update nft
        log.info(response["onChain"]["status"])
        response = contracts.check_minting_status(nft_id, collection_id)
        time.sleep(10)

    db.update_mint(internal_id, response["onChain"]["mintHash"])
    log.error("It is WORKING!!!")
    # TODO: update


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


@api.post(
    "/mint_nft/",
    dependencies=[Depends(JWTBearer())],
)
async def mint_nft(
    vk_id: int,
    nft_id: int,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
):
    token = get_token(authorization)
    log.info(authpair.get(token))
    wallet_addr = db.get_user_wallet(vk_id)
    db_nft = db.get_nft(nft_id)
    log.warning(db_nft.mintImage)
    db_event = db.get_event(db_nft.eventId)
    response = await contracts.mint_nft(
        db_event["collection_id"],
        db_nft.title,
        db_nft.description,
        db_nft.mintImage,
        wallet_addr,
        json.loads(db_nft.properties),
    )
    log.info(response)
    nft_hash = response["id"]

    background_tasks.add_task(
        update_nft_status, (nft_id, nft_hash, db_event["collection_id"])
    )
    return {"status": "ok"}


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
        event.title, event.description, event.image
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


@api.get("/get/event", dependencies=[Depends(JWTBearer())], tags=["event"])
async def get_event_by_id(event_id: int):
    return db.get_event(event_id)


@api.get(
    "/get/event/nfts",
    dependencies=[Depends(JWTBearer())],
    tags=["event"],
    response_model=list[TicketResponseSchema],
)
async def get_event_nft(event_id: int):
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
