"""Document upload and processing - placeholder for Module 4."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_documents():
    """Placeholder: will list documents after ingestion pipeline."""
    return {"message": "Documents module not yet implemented"}
