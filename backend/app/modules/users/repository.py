# Repository logic for the users module will be added in later steps.
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import User


def get_user_by_supabase_user_id(db: Session, supabase_user_id: str) -> User | None:
    stmt = select(User).where(User.supabase_user_id == supabase_user_id)
    return db.scalar(stmt)


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def create_user(db: Session, email: str, supabase_user_id: str | None = None) -> User:
    user = User(email=email, supabase_user_id=supabase_user_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def link_user_to_supabase_identity(db: Session, user: User, supabase_user_id: str) -> User:
    user.supabase_user_id = supabase_user_id
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
