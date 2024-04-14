from datetime import timedelta, timezone

from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import set_committed_value


def get_hours_between_dates(start_date, end_date) -> set[int]:
    current_date = start_date
    hours = set()
    while current_date < end_date:
        hours.add(current_date.hour)
        current_date += timedelta(hours=1)
    return hours


class RoomReservation(Base):
    __tablename__ = "room_reservation"

    id = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Foreign keys
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Foreign
    room: Mapped["Room"] = relationship(back_populates="reservations")
    user: Mapped["User"] = relationship(back_populates="reservations")

    def get_hours_in_common(self, start_date, end_date) -> set[int]:
        return get_hours_between_dates(self.start_date, self.end_date).intersection(
            get_hours_between_dates(start_date, end_date)
        )
