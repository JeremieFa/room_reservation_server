from datetime import datetime, timezone

from db.models.room_reservations import RoomReservation
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, validator

from .rooms import RoomDTO
from .users import UserDTO


class RoomReservationDTO(BaseModel):
    id: int
    user: UserDTO
    room: RoomDTO
    start_date: datetime
    end_date: datetime

    @field_validator("start_date", "end_date")
    def validate_dates(cls, dt, values):
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def __init__(self, reservation: RoomReservation):
        super().__init__(
            start_date=reservation.start_date,
            end_date=reservation.end_date,
            id=reservation.id,
            user=UserDTO(reservation.user),
            room=RoomDTO(reservation.room),
        )


class RoomReservationsWithPagination(BaseModel):
    reservations: list[RoomReservationDTO]
    total: int
    limit: int
    page: int

    def __init__(
        self,
        reservations: list[RoomReservation],
        total: int,
        limit: int,
        page: int,
    ):
        super().__init__(
            reservations=[
                RoomReservationDTO(reservation) for reservation in reservations
            ],
            total=total,
            limit=limit,
            page=page,
        )


class RoomReservationSimpleRequest(BaseModel):
    start_date: datetime
    end_date: datetime


class RoomReservationSummaryForADay(BaseModel):
    id: int
    name: str
    reservations: list[RoomReservationDTO]

    def __init__(
        self, room_id: int, room_name: str, reservations: list[RoomReservation]
    ):
        super().__init__(
            id=room_id,
            name=room_name,
            reservations=[
                RoomReservationDTO(reservation) for reservation in reservations
            ],
        )
