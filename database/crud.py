from sqlalchemy.orm import Session
from models.models import User, Observations


def create_user(
        db: Session,
        user_id: int,
        tg_id: int,
        username: str | None,
        first_name: str | None
):
    pass


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_observation(
        db: Session,
        id: int,
        tg_id: int,
        photo_url: str,
        model_result: str
):
    pass