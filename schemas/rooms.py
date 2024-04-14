from db.models.rooms import Room
from pydantic import BaseModel


class RoomDTO(BaseModel):
    id: int
    name: str

    def __init__(self, room: Room):
        super().__init__(id=room.id, name=room.name)
