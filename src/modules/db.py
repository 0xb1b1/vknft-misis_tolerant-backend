#!/usr/bin/env python3
# region Dependencies
from datetime import date, datetime, timedelta
from os import getenv
from time import sleep
from sqlalchemy.orm import sessionmaker
from modules.models import Base, User, Event, UserAllowlist, NFT
from sqlalchemy import create_engine
from typing import List, Union
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from psycopg2 import OperationalError as psycopg2OpError
# endregion


class DBManager:
    def __init__(self, log):
        self.pg_user = getenv('PG_USER')
        self.pg_pass = getenv('PG_PASS')
        self.pg_host = getenv('PG_HOST')
        self.pg_port = getenv('PG_PORT')
        self.pg_db   = getenv('PG_DB')
        self.log = log
        connected = False
        while not connected:
            try:
                self._connect()
            except (sqlalchemyOpError, psycopg2OpError):
                sleep(2)
            else:
                connected = True
        self._update_db()

    def __del__(self):
        """Close the database connection when the object is destroyed"""
        self._close()


    # region Connection setup
    def _connect(self) -> None:
        """Connect to the postgresql database"""
        self.engine = create_engine(f'postgresql+psycopg2://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}',
                                    pool_pre_ping=True)
        Base.metadata.bind = self.engine
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def _close(self) -> None:
        """Closes the database connection"""
        self.session.close_all()

    def _recreate_tables(self) -> None:
        """Recreate tables in DB"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def _update_db(self) -> None:
        """Create the database structure if it doesn't exist (update)"""
        # Create the tables if they don't exist
        Base.metadata.create_all(self.engine)
        #! Create required tables here
    # endregion

    def user_exists(self, vk_id: int) -> bool:
        """Check if user exists in the database"""
        return self.session.query(User).filter_by(vk_id=vk_id).first() is not None

    def get_users(self) -> dict:
        """Get all users from the database"""
        users = self.session.query(User).all()
        return { user.vk_id:
                 {
                   'wallet_public_key': user.wallet_public_key,
                   'first_name': user.first_name,
                   'last_name': user.last_name
                 }
            for user in users}

    def auth(self, vk_id: int, wallet_public_key: str, first_name: str, last_name: str) -> bool:
        """Create a new user in the database
        Returns True if the user exists, else False"""
        if self.user_exists(vk_id):
            self.update_user_wallet(vk_id, wallet_public_key)
            return True
        new_user = User(vk_id=vk_id, first_name=first_name, last_name=last_name, wallet_public_key=wallet_public_key)
        self.session.add(new_user)
        self.session.commit()
        return False

    def update_user_wallet(self, vk_id: int, wallet_public_key: str) -> None:
        """Update user wallet if it's different from the one in the database"""
        user = self.session.query(User).filter_by(vk_id=vk_id).first()
        if user.wallet_public_key != wallet_public_key:
            user.wallet_public_key = wallet_public_key
        self.session.commit()

    def get_user_wallet(self, vk_id: int) -> str:
        """Get user wallet from the database"""
        return self.session.query(User).filter_by(vk_id=vk_id).first().wallet_public_key

