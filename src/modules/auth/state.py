#!/usr/bin/env python3

class AuthPair:
    def __init__(self):
        self.store = {}  # {token: user_id}

    def store(self, token, user_id):
        self.store[token] = user_id

    def get(self, token):
        return self.store.get(token)