from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# File-based SQLite so a local backend can be used by a React frontend.
DATABASE_URL = "sqlite:///scu_forums.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


def init_db():
    # create tables
    Base.metadata.create_all(bind=engine)
