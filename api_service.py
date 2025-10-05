"""
Compatibility wrapper so the existing uvicorn invocation
`uvicorn api_service:app --reload` works whether you run it from
the project root or from the `backend/` directory.

It tries to import the FastAPI `app` from `backend.api_server` first
(when running from project root), and falls back to importing
`api_server` directly (when running with cwd=backend).
"""
try:
    # When running uvicorn from project root: `uvicorn api_service:app`
    from backend.api_service import app  # type: ignore
except Exception:
    # When running from within the backend directory: `uvicorn api_service:app`
    from api_server import app  # type: ignore

__all__ = ["app"]
