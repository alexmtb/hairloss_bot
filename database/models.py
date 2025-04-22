from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from session import engine
from base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, tg_id='{self.tg_id}', created_at='{self.created_at}')>"
    

class Observations(Base):
    __tablename__ = 'observations'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    tg_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.tg_id'), index=True)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    model_result: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Observation(tg_id='{self.tg_id}', created_at='{self.model_result}')>"


class ModelVersion(Base):
    __tablename__ = 'model_versions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ModelVersion(version='{self.version}', created_at='{self.created_at}')>"
    

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)



    


    




    