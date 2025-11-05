from backend.db import SessionLocal, engine, Base
from backend.object_registry import _REGISTRY


def cleanup_db():
    # Drop and recreate all tables to ensure a clean slate.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Close any open sessions by removing scoped_session registry
    try:
        SessionLocal.remove()
    except Exception:
        pass
    # Clear in-memory registry to avoid cross-test contamination
    _REGISTRY.clear()
    # print("[DEBUG] Database dropped and recreated; registry cleared.")

if __name__ == "__main__":
    cleanup_db()
