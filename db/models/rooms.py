from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from db.models.room_reservations import RoomReservation


class Room(Base):
    __tablename__ = "room"

    id = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, unique=True, nullable=False)

    # Foreign
    reservations: Mapped[List[RoomReservation]] = relationship()
