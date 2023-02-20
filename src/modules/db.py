#!/usr/bin/env python3
# region Dependencies
import asyncio
import json
import string
from random import choice
from datetime import date, datetime, timedelta
from os import getenv
from time import sleep, mktime
from sqlalchemy.orm import sessionmaker
from modules.models import Base, User, Event, UserAllowlist, NFT
from modules.auth.model import (
    UserLoginSchema,
    UserSimpleLoginSchema,
    EventCreateSchema,
    TicketCreateSchema,
    TicketResponseSchema,
)
from sqlalchemy import create_engine
from typing import List, Union
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from psycopg2 import OperationalError as psycopg2OpError
import requests as req

from modules.nftimage.nftimage import NFTImage

# endregion


class DBManager:
    def __init__(self, log, itools):
        self.pg_user = getenv("PG_USER")
        self.pg_pass = getenv("PG_PASS")
        self.pg_host = getenv("PG_HOST")
        self.pg_port = getenv("PG_PORT")
        self.pg_db = getenv("PG_DB")
        self.log = log
        self.nftimage = NFTImage()
        self.itools = itools
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
        self.engine = create_engine(
            f"postgresql+psycopg2://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}",
            pool_pre_ping=True,
        )
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

    # endregion

    def user_exists(self, vk_id: int) -> bool:
        """Check if user exists in the database"""
        return self.session.query(User).filter_by(vk_id=vk_id).first() is not None

    def get_users_test(self) -> dict:
        """Get all users from the database"""
        users = self.session.query(User).all()
        return {
            user.vk_id: {
                "wallet_public_key": user.wallet_public_key,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            for user in users
        }

    def get_users(self) -> dict:
        """Get all users from the database"""
        users = self.session.query(User).all()
        return {
            user.vk_id: {
                "wallet_public_key": user.wallet_public_key,
            }
            for user in users
        }

    def auth(
        self, vk_id: int, wallet_public_key: str, first_name: str, last_name: str
    ) -> bool:
        """Create a new user in the database
        Returns True if successful, False if user is not found and no wallet is provided"""
        user_exists = self.user_exists(vk_id)
        if not wallet_public_key and not user_exists:
            return False
        if not first_name and not user_exists:
            return False
        if not last_name and not user_exists:
            return False
        if user_exists:
            if wallet_public_key:
                self.update_user_wallet(vk_id, wallet_public_key)
            return True
        new_user = User(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            wallet_public_key=wallet_public_key,
        )
        self.session.add(new_user)
        self.session.commit()
        return True

    def update_user_wallet(self, vk_id: int, wallet_public_key: str) -> None:
        """Update user wallet if it's different from the one in the database"""
        user = self.session.query(User).filter_by(vk_id=vk_id).first()
        if user.wallet_public_key != wallet_public_key:
            user.wallet_public_key = wallet_public_key
        self.session.commit()

    def get_user_wallet(self, vk_id: int) -> str:
        """Get user wallet from the database"""

        return (
            self.session.query(User)
            .filter_by(vk_id=vk_id)
            .one_or_none()
            .wallet_public_key
        )

    def get_user_first_name(self, vk_id: int) -> str:
        """Get user first name from the database"""
        return self.session.query(User).filter_by(vk_id=vk_id).one_or_none().first_name

    def get_user_last_name(self, vk_id: int) -> str:
        """Get user last name from the database"""
        return self.session.query(User).filter_by(vk_id=vk_id).one_or_none().last_name

    def create_event(
        self,
        event_data: EventCreateSchema,
        user_id: int,
        collection_id: str,
    ):
        db_event = Event(
            title=event_data.title,
            description=event_data.description,
            place=event_data.place,
            image=event_data.image,
            ownerID=self.session.query(User).filter(User.id == user_id).one_or_none(),
            datetime=event_data.datetime,
            collectionID=collection_id,
        )
        self.session.add(db_event)
        self.session.commit()
        return db_event

    def create_nft(self, ticket_data: TicketCreateSchema) -> NFT:
        orig_img_b = req.get(ticket_data.image).content
        blur_img_b = self.nftimage.blur(orig_img_b)
        mint_img_b = self.nftimage.watermark(
            self.nftimage.darken(self.nftimage.blur(orig_img_b))
        )
        # encr_img_b = self.nftimage.encrypt(mint_img_b, 'super_secret_password')
        # orig_img = self.itools.upload(orig_img_b)
        blur_img = self.itools.upload(blur_img_b)
        mint_img = self.itools.upload(mint_img_b)
        db_nft = NFT(
            title=ticket_data.name,
            description=ticket_data.description,
            mintImage=mint_img,
            blurredImage=blur_img,
            properties=json.dumps(ticket_data.keys),
            eventId=ticket_data.eventId,
            imageKey="".join(
                choice(string.ascii_uppercase + string.digits) for _ in range(20)
            ),
        )
        self.session.add(db_nft)
        self.session.commit()
        return db_nft

    def get_nft(self, nft_id) -> NFT | None:
        return self.session.query(NFT).filter(NFT.id == nft_id).one_or_none()

    def update_mint(self, nft_id: int, mintHash: str):
        db_nft = self.get_nft(nft_id)
        db_nft.mintHash = mintHash
        self.session.add(db_nft)
        self.session.refresh(db_nft)
        self.session.commit()

    def get_nfts(self, event_id: int) -> list[TicketResponseSchema]:
        db_tickets = self.session.query(NFT).filter(NFT.eventId == event_id)
        return [TicketResponseSchema.from_orm(ticket) for ticket in db_tickets if ticket.mintHash == ""]

    def get_event(self, event_id: int) -> dict:
        event = self.session.query(Event).filter(Event.id == event_id).one_or_none()
        return {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "image": event.image,
            "datetime": mktime(event.datetime.timetuple()),
            "tickets": event.tickets,
            "collection_id": event.collectionID,
            "place": event.place,
            "owner_id": event.ownerID,
            "allowlist": event.allowList,
        }

    def get_events(self) -> List[dict]:
        """{ event_id: {'title': title, 'description': description, 'time': timestamp, 'tickets': [tickets], 'collection_id': collectionID, 'place': place, 'owner_id': ownerID, 'allowlist': allowList} }"""
        # Get all events from DB
        events = self.session.query(Event)
        # Prepare the result
        result = []
        for event in events:
            result.append(
                {
                    "event_id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "datetime": mktime(event.datetime.timetuple()),
                    "tickets": event.tickets,
                    "collection_id": event.collectionID,
                    "image": event.image,
                    "place": event.place,
                    "owner_id": event.ownerID,
                    "allowlist": event.allowList,
                }
            )
        return result

    def get_event_allowlist(self, event_id: int) -> List[int]:
        """[vk_id]"""
        # Get event from DB
        event = self.session.query(Event).filter_by(id=event_id).first()
        # Prepare the result
        result = []
        for user in event.allowlist:
            result.append(user.vk_id)
        return result
