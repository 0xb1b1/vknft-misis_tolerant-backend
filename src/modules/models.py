from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer)
    wallet_public_key = Column(String(44))
    first_name = Column(String(50))
    last_name = Column(String(50))

    events = relationship("Event", backref="owner")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(200))
    datetime = Column(DateTime)
    tickets = Column(ARRAY(Integer))
    collectionID = Column(String)
    place = Column(String(150))
    ownerID = Column(Integer, ForeignKey("users.id"))
    # allowList is a list of user IDs
    allowList = Column(ARRAY(Integer))

    user_allowlist = relationship("UserAllowlist", backref="events")
    nft = relationship("NFT", uselist=False, backref="events")


class UserAllowlist(Base):
    __tablename__ = "user_allowlists"

    user_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))


class NFT(Base):
    __tablename__ = "nfts"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(200))
    attended = Column(Boolean, default=False)
    mintImage = Column(String(300), default="")
    blurredImage = Column(String(300), default="")
    encryptedImage = Column(String(300), default="")
    properties = Column(String(500))
    mintHash = Column(String(70), default="")
    imageKey = Column(String(20))
    eventId = Column(Integer, ForeignKey("events.id"))


# class Token(Model):
#     id = fields.IntField(pk=True)
#     login_token = fields.CharField(max_length=2048)
#     is_used = fields.BooleanField(default=False)
