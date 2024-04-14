import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ALGORITHM", 180)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ["http://localhost:5173"])

DB_URL = os.getenv("DB_URL", "sqlite:///../db.db")
