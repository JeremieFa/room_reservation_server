from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from auth_helpers import get_current_user
from db.models.users import User
from db.repositories.room_reservations import (
    delete_room_reservation,
    get_room_reservation_by_id,
)
from db.session import get_db

room_reservations_router = APIRouter()


@room_reservations_router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
async def delete_reservation(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    reservation_id: int = Path(..., title="Reservation ID", ge=1),
):
    reservation = get_room_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation not found"
        )

    # put the reservation in the UTC timezone (if it's not already)
    # this is necessary because times are stored in the database without timezone as UTC
    if (
        reservation.end_date.tzinfo is None
        or reservation.end_date.tzinfo.utcoffset(reservation.end_date) is None
    ):
        reservation.end_date = reservation.end_date.replace(tzinfo=timezone.utc)

    if reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not allowed to delete this reservation",
        )

    # check if the reservation is not past
    # should be done in pydantic schema
    if reservation.end_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't delete a past reservation",
        )

    delete_room_reservation(db, reservation)
    return {"message": "Reservation deleted"}
