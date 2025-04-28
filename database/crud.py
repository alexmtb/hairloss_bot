from sqlalchemy.orm import Session
from .models import User, Observations


def get_or_create_user(
        db: Session,
        user_id: int,
        tg_id: int,
        username: str | None,
        first_name: str | None
) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        user = User(
            id=user_id,
            tg_id=tg_id,
            username=username,
            first_name=first_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def create_observation(
        db: Session,
        id: int,
        tg_id: int,
        photo: str,
        model_result: str
):
    observation = Observations(
        id=id,
        tg_id=tg_id,
        photo=photo,
        model_result=model_result
	)
    db.add(observation)
    db.commit()
    db.refresh(observation)
    
    return observation
