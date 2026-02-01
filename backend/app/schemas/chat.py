"""Chat request/response schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    text: str
    metadata: dict


class ChatResponse(BaseModel):
    response: str
    sources: list[SourceItem]


class ChatHistoryItem(BaseModel):
    id: int
    question: str
    response: str
    timestamp: str  # ISO format


class ChatHistoryResponse(BaseModel):
    items: list[ChatHistoryItem]
