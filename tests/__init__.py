# Ensure test DB is clean at start and before each individual test method
try:
    from backend.cleanup_db import cleanup_db
    # Initial cleanup before discovery
    cleanup_db()

    # Wrap unittest.TestCase.run to perform cleanup before each test method runs
    import unittest as _unittest
    _orig_run = _unittest.TestCase.run

    def _cleaning_run(self, result=None):
        try:
            cleanup_db()
        except Exception:
            pass
        return _orig_run(self, result)

    _unittest.TestCase.run = _cleaning_run
except Exception:
    # If cleanup is not available, ignore (tests may run in other contexts)
    pass
