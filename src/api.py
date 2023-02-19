#!/usr/bin/env python3

from fastapi import FastAPI, Body, Depends, Header

from modules.auth.model import PostSchema, UserSchema, UserLoginSchema
from modules.auth.handler import signJWT
from modules.auth.bearer import JWTBearer

import logging                    # Logging important events
from dotenv import load_dotenv    # Load environment variables from .env
from os import getenv             # Get environment variables
from modules.db import DBManager  # Database manager
from modules import contracts     # Smart contracts
from modules.auth.state import AuthPair


# region Logging
# Create a logger instance
log = logging.getLogger('backend')
# Create log formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Сreate console logging handler and set its level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# region Docker check
# Check if we are under Docker
DOCKER_MODE = False
if getenv("DOCKER_MODE") == 'true':
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
logging_level_lower = getenv('LOGGING_LEVEL').lower()
if logging_level_lower == 'debug':
    log.setLevel(logging.DEBUG)
    log.critical("Log level set to debug")
elif logging_level_lower == 'info':
    log.setLevel(logging.INFO)
    log.critical("Log level set to info")
elif logging_level_lower == 'warning':
    log.setLevel(logging.WARNING)
    log.critical("Log level set to warning")
elif logging_level_lower == 'error':
    log.setLevel(logging.ERROR)
    log.critical("Log level set to error")
elif logging_level_lower == 'critical':
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

# region Helper functions
def check_user(data: UserLoginSchema):
    """Log in via VK ID"""
    if db.auth(data.vk_id, data.wallet_public_key):
        return True
    else:
        return False
# endregion

# region Endpoints
@api.get("/", tags=["root"])
async def root():
    return {"message": "I love NFTs!"}

@api.post("/auth/register", tags=["auth"])
async def register(user: UserSchema = Body(...)):
    #users.append(user) # replace with db call, making sure to hash the password first
    db.auth(user.vk_id,
            user.wallet_public_key,
            user.first_name,
            user.last_name)
    return signJWT(user.vk_id)


@api.post("/auth/login", tags=["auth"])
async def login(user: UserLoginSchema = Body(...)):
    token = signJWT(user.vk_id)
    # Store the token in authpair
    authpair.store(token["access_token"], user.vk_id)

# region Protected
@api.get("/get/nfts", dependencies=[Depends(JWTBearer())], tags=["user", "nft"])
async def get_nfts(authorization: str = Header(None)):
    #return await contracts.get_all_nfts(authpair.get())
    return authorization
# endregion
# endregion

# region Tests
@api.get("/test/get_users", tags=["tests"])
async def get_users():
    return db.get_users()

@api.post("/test/secure", dependencies=[Depends(JWTBearer())], tags=["tests"])
async def test_secure():
    return {"message": "You are authorized!"}
# endregion
# endregion
