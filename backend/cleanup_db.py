from backend.db import SessionLocal, engine, Base
from backend.object_registry import _REGISTRY
# Ensure models are imported so metadata knows about all tables/columns
import backend.models  # noqa: F401

'''
Test file used to wipe DB
'''

def cleanup_db():
    # Drop existing tables and recreate with current model definitions (including any new columns)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        SessionLocal.remove()
    except Exception:
        pass
    _REGISTRY.clear()

if __name__ == "__main__":
    cleanup_db()
