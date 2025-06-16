# Emotional Chatbot API - Phase 1

A Python FastAPI backend for an emotional chatbot system with orchestrator-managed agent switching.

## Current Phase: Foundation (Phase 1)

✅ **Implemented:**
- Basic FastAPI application with OpenAI GPT-4o mini integration
- Single "Normal" agent with balanced responses
- Basic orchestrator for conversation management
- In-memory conversation storage
- RESTful API endpoints for chat functionality

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Make sure your `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application

**Easy way (recommended):**
```bash
./startup.sh
```

**Manual way:**
```bash
python main.py
```

The API will be available at `http://localhost:7878`

## API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
    "message": "Hello! How are you today?",
    "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
    "response": "Hello! I'm doing well, thank you for asking...",
    "conversation_id": "uuid-string",
    "agent_type": "normal",
    "timestamp": "2024-01-01T12:00:00"
}
```

### Get Conversation History
```http
GET /conversations/{conversation_id}
```

### Health Check
```http
GET /health
```

### Root Info
```http
GET /
```

## Testing

### Option 1: Web UI (Recommended)
1. Start the server: `./startup.sh`
2. Open `index.html` in your browser
3. Chat with the bot using the beautiful web interface!

### Option 2: Command Line Test
Run the test script to verify everything works:
```bash
python test_chat.py
```

**Note:** Make sure the server is running first with `./startup.sh`

## Architecture (Phase 1)

```
User Input → Basic Orchestrator → Normal Agent → Response
```

## Upcoming Phases

- **Phase 2:** Add Sentiment Analysis Agent
- **Phase 3:** Add Happy Agent with routing logic
- **Phase 4:** Complete all base emotions (Happy, Angry, Sad)
- **Phase 5:** Implement emotion levels (happy1, happy2, happy3, etc.)

## Project Structure

```
├── main.py              # Main FastAPI application
├── index.html           # Web UI for testing the chatbot
├── test_chat.py         # Test script
├── startup.sh           # Easy startup script with port management
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Features

- **Conversation Management:** Each conversation has a unique ID and maintains history
- **OpenAI Integration:** Uses GPT-4o mini for all responses
- **CORS Enabled:** Ready for frontend integration
- **Error Handling:** Proper HTTP status codes and error messages
- **Async Support:** Fully asynchronous for better performance
- **Smart Startup Script:** Aggressive port management and dependency checking

## Startup Script Features

The `startup.sh` script provides:
- **Aggressive Port Killing:** Multiple methods to ensure port 7878 is free
- **Dependency Checking:** Automatically installs missing packages
- **Environment Validation:** Checks for .env file
- **Clear Status Messages:** Shows exactly what's happening
- **Error Handling:** Graceful failure with helpful messages 