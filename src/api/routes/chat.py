"""
Chat Routes

Endpoints for agent chat interactions.
Used by Qlik embedded chat and API clients.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Chat request from client."""
    message: str = Field(..., description="User's message or question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Optional[dict] = Field(None, description="Qlik context (selected facility, filters, etc.)")


class ChatResponse(BaseModel):
    """Chat response to client."""
    response: str = Field(..., description="Agent's response")
    session_id: str = Field(..., description="Session ID for follow-up")
    tools_used: list[str] = Field(default_factory=list, description="Tools used to generate response")
    sources: list[str] = Field(default_factory=list, description="Data sources referenced")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


# -----------------------------------------------------------------------------
# Session Management
# -----------------------------------------------------------------------------

# In-memory session storage (replace with Redis for production)
_sessions: dict[str, dict] = {}


def get_or_create_session(session_id: Optional[str]) -> tuple[str, dict]:
    """Get existing session or create new one."""
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]
    
    new_id = str(uuid.uuid4())
    _sessions[new_id] = {"history": []}
    return new_id, _sessions[new_id]


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return agent response.
    
    This is the main endpoint for Qlik embedded chat.
    """
    logger.info(f"Chat request: {request.message[:100]}...")
    
    # Get or create session
    session_id, session = get_or_create_session(request.session_id)
    
    try:
        # TODO: Implement actual agent execution
        # 1. Build context from Qlik selections
        # 2. Execute agent with guardrails
        # 3. Return response
        
        # Placeholder response
        response_text = (
            f"I received your question: '{request.message}'. "
            f"Agent implementation pending."
        )
        
        # Update session history
        session["history"].append({"role": "user", "content": request.message})
        session["history"].append({"role": "assistant", "content": response_text})
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            tools_used=[],
            sources=[],
            execution_time=0.1,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "cleared"}
    return {"status": "not_found"}


@router.post("/admin/clear-sessions")
async def clear_all_sessions():
    """Clear all chat sessions (admin endpoint)."""
    count = len(_sessions)
    _sessions.clear()
    return {"status": "cleared", "sessions_cleared": count}
