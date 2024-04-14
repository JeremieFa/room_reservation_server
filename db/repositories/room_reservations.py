from datetime import date, datetime

from db.models.room_reservations import RoomReservation
from db.models.rooms import Room
from db.models.users import User
from sqlalchemy import desc
from sqlalchemy.orm import Session


def get_all_reservation_by_user(
    db: Session, user: User, limit: int, page: int
) -> tuple[list[RoomReservation], int, int, int]:
    reservations_query = db.query(RoomReservation).filter(
        RoomReservation.user_id == user.id
    )

    total = reservations_query.count()

    reservations = (
        reservations_query.order_by(desc(RoomReservation.start_date))
        .limit(limit)
        .offset(page * limit)
        .all()
    )
    return reservations, total, limit, page


def get_all_reservation_on_room_between_dates(
    db: Session, room: Room, start_date, end_date
) -> list[RoomReservation]:
    return (
        db.query(RoomReservation)
        .filter(RoomReservation.room_id == room.id)
        .filter(RoomReservation.start_date < end_date)
        .filter(RoomReservation.end_date > start_date)
        .all()
    )


def create_room_reservation(
    db: Session, room: Room, user: User, start_date: datetime, end_date: datetime
) -> RoomReservation:
    reservation = RoomReservation(
        room_id=room.id, user_id=user.id, start_date=start_date, end_date=end_date
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def delete_room_reservation(db: Session, reservation: RoomReservation):
    db.delete(reservation)
    db.commit()


def get_room_reservation_by_id(
    db: Session, reservation_id: int
) -> RoomReservation | None:
    return (
        db.query(RoomReservation).filter(RoomReservation.id == reservation_id).first()
    )


def get_all_rooms_reservations_between_dates(
    db: Session, start_date: date, end_date: date
) -> list[RoomReservation]:

    return (
        db.query(RoomReservation)
        .filter(RoomReservation.start_date < end_date)
        .filter(RoomReservation.end_date > start_date)
        .order_by(RoomReservation.start_date)
        .all()
    )
