from typing import List

from db.base_class import Base
from db.models.room_reservations import RoomReservation
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Foreign
    reservations: Mapped[List[RoomReservation]] = relationship()
