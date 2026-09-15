import os
import json
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

from database import SessionLocal, Session as DBSession, Message as DBMessage, init_db, engine
from agent import generate_response

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt)
        }
        return json.dumps(log_obj)

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

app = FastAPI(title="Lenny Growth Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: List[str]
    skill_used: str

class SessionResponse(BaseModel):
    session_id: str

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health_check():
    provider = os.getenv('LLM_PROVIDER', 'local')
    db_status = 'disconnected'
    try:
        with engine.connect() as conn:
            db_status = 'connected'
    except Exception:
        pass
    
    return {
        "status": "ok",
        "llm_provider": provider,
        "database": db_status
    }

@app.get("/config")
def get_config():
    provider = os.getenv('LLM_PROVIDER', 'local')
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'phi3')
    model = 'claude-3-haiku-20240307' if provider.lower() == 'cloud' else ollama_model
    return {
        "llm_provider": provider,
        "ollama_base_url": ollama_url,
        "model": model
    }

@app.post("/sessions", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    try:
        new_session = DBSession()
        db.add(new_session)
        db.commit()
        return {"session_id": new_session.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Error creating session")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    if not session_id:
        try:
            new_session = DBSession()
            db.add(new_session)
            db.commit()
            session_id = new_session.id
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating session for chat: {e}")
            raise HTTPException(status_code=500, detail="Error establishing session")
    
    try:
        user_msg = DBMessage(session_id=session_id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()
        
        db_history = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.created_at).all()
        chat_history = []
        for msg in db_history[:-1]:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            else:
                chat_history.append(AIMessage(content=msg.content))
                
        reply, sources, skill = generate_response(request.message, chat_history)
        
        assistant_msg = DBMessage(session_id=session_id, role="assistant", content=reply)
        db.add(assistant_msg)
        db.commit()
        
        logger.info(f"Processed chat for session {session_id} using skill {skill}")
        
        return ChatResponse(
            session_id=session_id,
            reply=reply,
            sources=sources,
            skill_used=skill
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
