from typing import Generator, Tuple
from fastapi import Query, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

def get_pagination(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)")
) -> Tuple[int, int]:
    """Dependency that extracts and validates pagination parameters."""
    return page, page_size
