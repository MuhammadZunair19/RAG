"""Chat and RAG: ask question, get answer with sources; chat history."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models import User, Chat as ChatModel
from app.schemas.chat import ChatRequest, ChatResponse, SourceItem, ChatHistoryItem, ChatHistoryResponse
from app.core.dependencies import get_current_user
from app.services.rag import rag_query

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a question; RAG retrieves context and returns answer with sources."""
    question = (body.question or "").strip()
    if not question:
        return ChatResponse(response="Please provide a question.", sources=[])

    response_text, sources = rag_query(question, top_k=5)
    source_items = [SourceItem(text=s["text"], metadata=s["metadata"]) for s in sources]

    chat_row = ChatModel(
        user_id=current_user.id,
        question=question,
        response=response_text,
    )
    db.add(chat_row)
    await db.flush()

    return ChatResponse(response=response_text, sources=source_items)


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current user's recent chat history."""
    result = await db.execute(
        select(ChatModel)
        .where(ChatModel.user_id == current_user.id)
        .order_by(ChatModel.timestamp.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    items = [
        ChatHistoryItem(
            id=r.id,
            question=r.question,
            response=r.response,
            timestamp=r.timestamp.isoformat() if r.timestamp else "",
        )
        for r in rows
    ]
    return ChatHistoryResponse(items=items)
