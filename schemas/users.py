from db.models.users import User
from pydantic import BaseModel


class UserDTO(BaseModel):
    id: int
    email: str

    def __init__(self, user: User):
        super().__init__(id=user.id, email=user.email)


class UserInDB(UserDTO):
    hashed_password: str

    def __init__(self, user: User):
        super().__init__(user)
        self.hashed_password = user.hashed_password


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserCreateRequest(BaseModel):
    email: str
    password: str

    # other fields can be added here
    # for example: first_name: str, last_name: str
