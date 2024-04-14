from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth_helpers import get_current_user
from db.models.users import User
from db.repositories.room_reservations import get_all_reservation_by_user
from db.session import get_db
from schemas.room_reservations import RoomReservationsWithPagination

users_router = APIRouter()


@users_router.get("/my-reservations", status_code=status.HTTP_200_OK)
async def get_my_reservations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    limit: int = 10,
    page: int = 0,
) -> RoomReservationsWithPagination:

    reservations, total, limit, page = get_all_reservation_by_user(
        db, current_user, limit, page
    )

    return RoomReservationsWithPagination(
        reservations=reservations,
        total=total,
        limit=limit,
        page=page,
    )
