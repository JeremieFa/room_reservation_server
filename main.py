from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import Base
from db.session import engine
from routers import auth_router, room_reservations_router, rooms_router, users_router
from settings import ALLOWED_HOSTS

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users")
app.include_router(rooms_router, prefix="/rooms")
app.include_router(room_reservations_router, prefix="/room-reservations")

app.include_router(auth_router)
