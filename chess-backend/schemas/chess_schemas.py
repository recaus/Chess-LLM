from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LegalMove(BaseModel):
    from_square: str = Field(..., alias="from") 
    to: str
    san: str
    promotion: Optional[str] = None
    class Config:
        validate_by_name = True

class ChessMoveRequest(BaseModel):
    fen: str
    playerMove: str
    humanPieceColor: str
    aiPieceColor: str
    legalMoves: List[LegalMove]

class LLMChatRequest(BaseModel):
    fen: str
    question: str

class LLMChatRequest(BaseModel):
    fen: str
    question: str
    history: List[Dict[str, str]]
