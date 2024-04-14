from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from auth_helpers import get_current_user
from db.models.users import User
from db.repositories.room_reservations import (
    create_room_reservation,
    get_all_reservation_on_room_between_dates,
    get_all_rooms_reservations_between_dates,
)
from db.repositories.rooms import (
    get_all_rooms,
    get_all_rooms_without_reservations_between_dates,
    get_room_by_id,
)
from db.session import get_db
from schemas.room_reservations import (
    RoomReservationDTO,
    RoomReservationSimpleRequest,
    RoomReservationSummaryForADay,
)
from schemas.rooms import RoomDTO

rooms_router = APIRouter()

ROOM_RESERVATION_CREATION_INVALID_DATES_ERROR = (
    "Invalid dates, start_date must be in futur, start_date must be before end_date and both must have "
    "minutes and seconds equal to 0"
)

ROOM_RESERVATION_CREATION_ALREADY_RESERVED_ERROR = (
    "Room is already reserved on the following hours: "
)
ROOM_RESERVATION_CREATION_DATES_NOT_AWARE_ERROR = (
    "Dates (start_date and end_date) must be aware and in UTC timezone"
)


@rooms_router.get("/", status_code=status.HTTP_200_OK)
async def get_all(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[RoomDTO]:
    rooms = get_all_rooms(db)
    return [RoomDTO(room) for room in rooms]


@rooms_router.post("/{room_id}/create-reservation", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    room_reservation: RoomReservationSimpleRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    room_id: int = Path(..., title="Room ID", ge=1),
    db: Session = Depends(get_db),
) -> RoomReservationDTO:
    """
    This endpoint will allow a user to create a reservation for a room.
    User must be authenticated to access this endpoint.
    If the room is already reserved at the same time, the endpoint will return a 400 error with a message indicating the hours
    """

    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Room not found"
        )

    # check if dates are aware and utc or rize an error
    if (
        room_reservation.start_date.tzinfo is None
        or room_reservation.start_date.tzinfo.utcoffset(room_reservation.start_date)
        is None
        or room_reservation.end_date.tzinfo is None
        or room_reservation.end_date.tzinfo.utcoffset(room_reservation.end_date) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ROOM_RESERVATION_CREATION_DATES_NOT_AWARE_ERROR,
        )

    # multiple checks
    # if the start_date if after now.
    # if the start_date is before the end_date.
    # if start_date is not at the beginning of an hour
    # and end_date is not at the beginning of an hour.
    # should be done in pydantic schema
    if (
        room_reservation.start_date < datetime.now(timezone.utc)
        or room_reservation.start_date >= room_reservation.end_date
        or room_reservation.start_date.minute != 0
        or room_reservation.start_date.second != 0
        or room_reservation.start_date.microsecond != 0
        or room_reservation.end_date.minute != 0
        or room_reservation.end_date.second != 0
        or room_reservation.end_date.microsecond != 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ROOM_RESERVATION_CREATION_INVALID_DATES_ERROR,
        )

    # check if there is already a reservation on this room at the same time
    reservations = get_all_reservation_on_room_between_dates(
        db, room, room_reservation.start_date, room_reservation.end_date
    )
    if reservations:
        common_hours = set()
        for reservation in reservations:
            common_hours.update(
                reservation.get_hours_in_common(
                    room_reservation.start_date, room_reservation.end_date
                )
            )

        error_msg = ROOM_RESERVATION_CREATION_ALREADY_RESERVED_ERROR
        error_msg += ", ".join([f"{hour}:00" for hour in common_hours])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # create reservation
    reservation = create_room_reservation(
        db, room, current_user, room_reservation.start_date, room_reservation.end_date
    )
    return RoomReservationDTO(reservation)


@rooms_router.get("/all-rooms-reservations", status_code=status.HTTP_200_OK)
async def get_all_rooms_reservations(
    start_date: datetime,
    end_date: datetime,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[RoomReservationSummaryForADay]:
    """
    This endpoint will return all the reservations for all the rooms for a given day.
    The endpoint will take one parameter:
    - date: the date for which we want to get the reservations.

    The user must be authenticated to access this endpoint.
    """

    rooms = get_all_rooms(db)

    reservations = get_all_rooms_reservations_between_dates(db, start_date, end_date)

    rooms_reservations_summary: list[RoomReservationSummaryForADay] = []
    for room in rooms:
        rooms_reservations_summary.append(
            RoomReservationSummaryForADay(
                room_id=room.id,
                room_name=room.name,
                reservations=[
                    reservation
                    for reservation in reservations
                    if reservation.room_id == room.id
                ],
            )
        )
    return rooms_reservations_summary


@rooms_router.get("/availables", status_code=status.HTTP_200_OK)
async def get_available_rooms(
    start_date: datetime,
    end_date: datetime,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[RoomDTO]:
    rooms = get_all_rooms_without_reservations_between_dates(db, start_date, end_date)
    available_rooms = [RoomDTO(room) for room in rooms]
    return available_rooms
