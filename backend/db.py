from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# File-based SQLite so a local backend can be used by a React frontend.
DATABASE_URL = "sqlite:///scu_forums.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


def init_db():
    # create tables
    Base.metadata.create_all(bind=engine)
    # Ensure new columns exist if added after initial creation
    inspector = inspect(engine)
    def ensure_column(table: str, column: str, ddl: str):
        cols = [c['name'] for c in inspector.get_columns(table)]
        if column not in cols:
            with engine.connect() as conn:
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {ddl}'))
                # Backfill existing rows
                if column == 'created_at':
                    conn.execute(text(f"UPDATE {table} SET {column}=CURRENT_TIMESTAMP WHERE {column} IS NULL"))
    try:
        ensure_column('forums', 'created_at', 'TIMESTAMP')
        ensure_column('posts', 'created_at', 'TIMESTAMP')
    except Exception:
        pass
