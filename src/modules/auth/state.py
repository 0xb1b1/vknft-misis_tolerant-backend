#!/usr/bin/env python3
from typing import Any


class AuthPair:
    def __init__(self):
        self.store = {}  # {token: user_id}

    def post(self, token, user_id):
        self.store[token] = user_id

    def get(self, token) -> Any:
        return self.store.get(token)
