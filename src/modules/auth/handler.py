#!/usr/bin/env python3

import time
from typing import Dict
from dotenv import load_dotenv
from os import getenv

import jwt
from decouple import config

load_dotenv()
JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")

def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 60*60*24*7
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
