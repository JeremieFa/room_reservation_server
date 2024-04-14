from sqlalchemy.orm import Session

from db.models.users import User


def save_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def find_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()
