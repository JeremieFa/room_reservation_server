from datetime import datetime

from db.models.room_reservations import RoomReservation
from db.models.rooms import Room
from sqlalchemy import not_
from sqlalchemy.orm import Session


def get_all_rooms(db: Session) -> list[Room]:
    return db.query(Room).all()


def get_room_by_id(db: Session, room_id: int) -> Room:
    return db.query(Room).filter(Room.id == room_id).first()


def get_all_rooms_without_reservations_between_dates(
    db: Session, start_date: datetime, end_date: datetime
) -> list[Room]:
    overlapping_reservations = (
        db.query(RoomReservation.room_id)
        .filter(
            RoomReservation.start_date < end_date, RoomReservation.end_date > start_date
        )
        .subquery()
    )
    return db.query(Room).filter(not_(Room.id.in_(overlapping_reservations))).all()


def create_room(db: Session, name: str) -> Room:
    room = Room(name=name)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
