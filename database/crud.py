from sqlalchemy.orm import Session
from .models import User, Observations


def get_or_create_user(
        db: Session,
        effective_user,
        chat_id
) -> User:
    """Saving user data to database"""
    # Используем именно tg_id для поиска, так как это наш уникальный ключ
    try:
        user = db.query(User).filter(User.tg_id == effective_user.id).first()
        
        if not user:
            user = User(
                tg_id = effective_user.id,
                username = effective_user.username,
                first_name = effective_user.first_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        # Попробуем еще раз получить пользователя
        print(f"Error creating user: {e}")
        user = db.query(User).filter(User.tg_id == effective_user.id).first()
        if user:
            return user
        raise e
 

def create_observation(
        db: Session,
        tg_id: int,
        photo: str,
        model_result: str
):
    try:
        observation = Observations(
            tg_id=tg_id,
            photo=photo,
            model_result=model_result
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)
        return observation
    except Exception as e:
        db.rollback()
        print(f"Error creating observation: {e}")
        raise e
