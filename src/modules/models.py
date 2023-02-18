from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, array
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    wallet_public_key = Column(String, nullable=True)
    created_events = relationship(
        "Event",
        backref="owner",
        lazy="dynamic",
        primaryjoin="User.id == Event.owner_id",
    )
    # whilisted_events = relationship(
    #     "Event",
    #     backref="owner",
    #     lazy="dynamic",
    #     primaryjoin="User.id == Event.owner_id",
    # )


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    auth_token = Column(String(2048))
    is_used = Column(Boolean)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(String(2048), default="")
    start_datetime = Column(DateTime(timezone=True), server_default=func.now())
    collection_id = relationship(
        "Collection",
        backref="events",
        lazy="dynamic",
        primaryjoin="Event.id == Collection.event_id",
    )
    # subnail
    # colection (ticket)

    owner_id = Column(Integer, ForeignKey("user.id"))


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(String(256), primary_key=True)
    onChain = Column(JSON)
    nft_metadata = Column(JSON)

    name = Column(String(256), nullable=False)
    image = Column(String(2048), default="")
    description = Column(String(2048), default="")
    attributes = Column(JSON)
    collection_id = Column(String, ForeignKey("colection.id"))


class Collection(Base):
    __tablename__ = "colection"

    id = Column(String(256), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(String(2048), default="")
    image_url = Column(String(2048), default="")
    nft_metadata = Column(JSON, nullable=True)
    onchain = Column(JSON, nullable=True)

    event_id = Column(Integer, ForeignKey("events.id"))
    tickets = relationship(
        "Ticket",
        backref="Collection",
        lazy="dynamic",
        primaryjoin="Collection.id == Ticket.collection_id",
    )


class WalletState(Base):
    __tablename__ = "walletstates"

    id = Column(Integer, primary_key=True)
    state = Column(String)


# class Token(Model):
#     id = fields.IntField(pk=True)
#     login_token = fields.CharField(max_length=2048)
#     is_used = fields.BooleanField(default=False)
