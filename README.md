# Emotional Chatbot API - Phase 2

A Python FastAPI backend for an emotional chatbot system with orchestrator-managed agent switching and sentiment analysis.

## Current Phase: Sentiment Analysis (Phase 2)

✅ **Implemented:**
- ✅ **Refactored Architecture**: Modular structure with separate agent classes
- ✅ **Sentiment Analysis Agent**: Detects emotions with thinking tags
- ✅ **Enhanced Orchestrator**: Processes sentiment data and makes routing decisions
- ✅ **External Prompts**: All agent personalities in markdown files
- ✅ **Thinking Tags**: Visible AI reasoning for sentiment analysis and orchestrator decisions
- ✅ **Enhanced Web UI**: Displays sentiment analysis with visual emotion bars
- ✅ **API v2.0**: Returns sentiment analysis and orchestrator decision data

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

## Architecture (Phase 2)

```
User Input → Sentiment Agent → Orchestrator → Normal Agent → Response
                ↓                    ↓
        Emotion Analysis    Routing Decision + Thinking
```

**Flow:**
1. **User Input**: Message received
2. **Sentiment Agent**: Analyzes emotion with thinking process
3. **Orchestrator**: Makes routing decision (currently always Normal agent)
4. **Normal Agent**: Generates response
5. **API Response**: Includes chat response + sentiment analysis + orchestrator thinking

## Upcoming Phases

- **Phase 3:** Add Happy Agent with routing logic (happy1, happy2, happy3)
- **Phase 4:** Complete all base emotions (Angry, Sad agents)
- **Phase 5:** Implement escalation/de-escalation logic
- **Phase 6:** Add jump logic for extreme emotions

## Project Structure

```
├── main.py              # Main FastAPI application
├── index.html           # Web UI for testing the chatbot
├── test_chat.py         # Test script
├── startup.sh           # Easy startup script with port management
├── requirements.txt     # Python dependencies
├── agents/              # Agent classes
│   ├── __init__.py
│   ├── base_agent.py    # Base agent class with common functionality
│   ├── normal_agent.py  # Normal agent implementation
│   └── sentiment_agent.py # Sentiment analysis agent
├── orchestrator/        # Orchestrator logic
│   ├── __init__.py
│   └── orchestrator.py  # Main orchestrator with routing logic
├── utils/               # Utility functions
│   ├── __init__.py
│   └── prompt_loader.py # External prompt loading
├── prompts/             # External agent prompts (markdown files)
│   ├── normal_agent.md  # Normal agent system prompt
│   ├── sentiment_agent.md # Sentiment analysis agent prompt
│   ├── happy_agent.md   # Happy agent system prompt (ready for Phase 3)
│   ├── angry_agent.md   # Angry agent system prompt (ready for Phase 4)
│   └── sad_agent.md     # Sad agent system prompt (ready for Phase 4)
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
- **External Prompts:** All agent personalities defined in external markdown files

## Startup Script Features

The `startup.sh` script provides:
- **Aggressive Port Killing:** Multiple methods to ensure port 7878 is free
- **Dependency Checking:** Automatically installs missing packages
- **Environment Validation:** Checks for .env file
- **Clear Status Messages:** Shows exactly what's happening
- **Error Handling:** Graceful failure with helpful messages 