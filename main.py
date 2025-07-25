# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

# Import refactored components
from orchestrator.orchestrator import Orchestrator
from agents.base_agent import ChatMessage as AgentChatMessage

app = FastAPI(title="Emotional Chatbot API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversations (replace with database later)
conversations = {}

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_type: str
    timestamp: datetime
    sentiment_analysis: Optional[Dict[str, Any]] = None
    orchestrator_decision: Optional[Dict[str, Any]] = None
    orchestrator_insights: Optional[Dict[str, Any]] = None

# Initialize orchestrator
orchestrator = Orchestrator()

@app.on_event("startup")
async def startup_event():
    """Reset orchestrator state on server startup"""
    print("🔄 Server starting up - resetting orchestrator state...")
    orchestrator.reset_state()  # Use the new reset method
    conversations.clear()
    print("✅ Orchestrator state reset complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on server shutdown"""
    print("🛑 Server shutting down - cleaning up state...")

@app.get("/")
async def root():
    return {"message": "Emotional Chatbot API is running!", "version": "2.0.0", "phase": "2 - Sentiment Analysis"}

@app.post("/chat-fast", response_model=ChatResponse)
async def chat_fast(request: ChatRequest):
    """Fast chat endpoint using combined sentiment+response approach"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            # Reset orchestrator state for new conversations
            print(f"🆕 New conversation {conversation_id[:8]}... - resetting orchestrator state")
            orchestrator.reset_state()
        
        conversation_history = conversations[conversation_id]
        
        # Add user message to history
        user_message = ChatMessage(
            role="user", 
            content=request.message,
            timestamp=datetime.now()
        )
        conversation_history.append(user_message)
        
        # Convert to agent format for processing
        agent_history = [
            AgentChatMessage(msg.role, msg.content, msg.timestamp) 
            for msg in conversation_history
        ]
        
        # Process message through orchestrator using PARALLEL approach (optimized)
        response_content, agent_type, analysis_data = await orchestrator.process_message(
            request.message, 
            agent_history
        )
        
        # Add assistant response to history
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now()
        )
        conversation_history.append(assistant_message)
        
        # Update conversation storage
        conversations[conversation_id] = conversation_history
        
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id,
            agent_type=agent_type,
            timestamp=datetime.now(),
            sentiment_analysis=analysis_data.get("sentiment_analysis"),
            orchestrator_decision=analysis_data.get("orchestrator_decision"),
            orchestrator_insights=analysis_data.get("orchestrator_insights")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            # Reset orchestrator state for new conversations
            print(f"🆕 New conversation {conversation_id[:8]}... - resetting orchestrator state")
            print(f"   Before reset: anger_points={orchestrator.anger_meter.anger_points}, agent={orchestrator.current_agent}")
            orchestrator.reset_state()
            print(f"   After reset: anger_points={orchestrator.anger_meter.anger_points}, agent={orchestrator.current_agent}")
        
        conversation_history = conversations[conversation_id]
        
        # Add user message to history
        user_message = ChatMessage(
            role="user", 
            content=request.message,
            timestamp=datetime.now()
        )
        conversation_history.append(user_message)
        
        # Convert to agent format for processing
        agent_history = [
            AgentChatMessage(msg.role, msg.content, msg.timestamp) 
            for msg in conversation_history
        ]
        
        # Process message through orchestrator
        response_content, agent_type, analysis_data = await orchestrator.process_message(
            request.message, 
            agent_history
        )
        
        # Add assistant response to history
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now()
        )
        conversation_history.append(assistant_message)
        
        # Update conversation storage
        conversations[conversation_id] = conversation_history
        
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id,
            agent_type=agent_type,
            timestamp=datetime.now(),
            sentiment_analysis=analysis_data.get("sentiment_analysis"),
            orchestrator_decision=analysis_data.get("orchestrator_decision"),
            orchestrator_insights=analysis_data.get("orchestrator_insights")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del conversations[conversation_id]
    return {"message": "Conversation deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/reset")
async def reset_state():
    """Reset orchestrator state and clear all conversations"""
    print("🔄 Manual state reset requested...")
    orchestrator.reset_state()  # Use the new reset method
    conversations.clear()
    print("✅ Manual state reset complete")
    return {
        "message": "State reset successfully", 
        "timestamp": datetime.now(),
        "current_agent": orchestrator.current_agent,
        "anger_counter": orchestrator.orchestrator_agent.anger_counter,
        "anger_points": orchestrator.anger_meter.anger_points
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7878) 