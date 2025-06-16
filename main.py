from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Emotional Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

class NormalAgent:
    """Normal agent with balanced, professional responses"""
    
    def __init__(self):
        self.system_prompt = """You are a helpful, balanced, and professional AI assistant. 
        Provide clear, informative, and friendly responses. Maintain a neutral but warm tone.
        Be helpful and engaging without being overly enthusiastic or emotional."""
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        try:
            # Convert messages to OpenAI format
            openai_messages = [{"role": "system", "content": self.system_prompt}]
            for msg in messages:
                openai_messages.append({"role": msg.role, "content": msg.content})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=openai_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

class BasicOrchestrator:
    """Basic orchestrator that manages conversation flow"""
    
    def __init__(self):
        self.normal_agent = NormalAgent()
    
    async def process_message(self, message: str, conversation_history: List[ChatMessage]) -> tuple[str, str]:
        """Process user message and return response with agent type"""
        # For Phase 1, always use normal agent
        response = await self.normal_agent.generate_response(conversation_history)
        return response, "normal"

# Initialize orchestrator
orchestrator = BasicOrchestrator()

@app.get("/")
async def root():
    return {"message": "Emotional Chatbot API is running!", "version": "1.0.0", "phase": "1 - Foundation"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversation_history = conversations[conversation_id]
        
        # Add user message to history
        user_message = ChatMessage(
            role="user", 
            content=request.message,
            timestamp=datetime.now()
        )
        conversation_history.append(user_message)
        
        # Process message through orchestrator
        response_content, agent_type = await orchestrator.process_message(
            request.message, 
            conversation_history
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
            timestamp=datetime.now()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7878) 