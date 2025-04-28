from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    "postgresql://postgres:44Ob0vvjfwnVBJtV@immortally-absolved-tuatara.data-1.use1.tembo.io:5432/postgres"
)
db_session = scoped_session(sessionmaker(bind=engine))