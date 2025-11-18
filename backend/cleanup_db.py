from backend.db import SessionLocal, engine, Base
from backend.object_registry import _REGISTRY

'''
Test file used to wipe DB
'''

def cleanup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        SessionLocal.remove()
    except Exception:
        pass
    _REGISTRY.clear()

if __name__ == "__main__":
    cleanup_db()
