from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Health and Database Connectivity Status")
def health_check(db: Session = Depends(get_db)):
    """
    Returns API runtime health and actively verifies SQLite database connectivity.
    """
    try:
        # Actually execute a query to verify database engine and connection
        db.execute(text("SELECT 1")).scalar()
        db_status = "connected"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )
    return {
        "status": "ok",
        "database": db_status
    }
