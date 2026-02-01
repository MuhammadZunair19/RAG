"""Document upload and list - admin only."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, Document as DocumentModel, EmbeddingMeta
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.core.dependencies import get_current_user, require_role
from app.services.ingestion import ingest_pdf

router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Upload a PDF; extract, chunk, embed, and store. Admin only."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large (max 20 MB)",
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    doc = DocumentModel(
        filename=file.filename or "document.pdf",
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    try:
        chunk_rows = ingest_pdf(content, doc.id, doc.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process PDF: {str(e)}",
        ) from e

    for chunk_text, page_number, chunk_index in chunk_rows:
        meta = EmbeddingMeta(
            document_id=doc.id,
            page_number=page_number,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
        )
        db.add(meta)

    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        chunks=len(chunk_rows),
        message="Document ingested successfully",
    )


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    """List all uploaded documents. Admin only."""
    from sqlalchemy import select
    result = await db.execute(select(DocumentModel).order_by(DocumentModel.upload_date.desc()))
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]
