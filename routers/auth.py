from typing import Annotated

from auth_helpers import Token, create_access_token_from_user, verify_password
from db.repositories.users import find_user_by_email
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserLoginRequest
from sqlalchemy.orm import Session

auth_router = APIRouter()


@auth_router.post("/api/auth", status_code=status.HTTP_200_OK)
async def login(
    login_request: UserLoginRequest, db: Session = Depends(get_db)
) -> Token:
    user = find_user_by_email(db, login_request.email)

    if user is not None:
        if verify_password(login_request.password, user.hashed_password):
            return create_access_token_from_user(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credentials are invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )


@auth_router.post("/auth")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """
    This endpoint will take the username and password and return an access token
    Used only for testing purposes with the swagger UI.
    """
    user = find_user_by_email(db, form_data.username)

    if user is not None:
        if verify_password(form_data.password, user.hashed_password):
            return create_access_token_from_user(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
