# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server Management
- **Start server**: `./startup.sh` (recommended) or `python main.py`
- **Server runs on**: `http://localhost:7878`
- **API documentation**: `http://localhost:7878/docs`
- **Web UI**: Open `index.html` or `chat-ui.html` in browser

### Testing
- **Run main chat test**: `python "test scripts/test_chat.py"`
- **Test specific agents**: Files in `test scripts/` directory for individual agent testing
- **Web UI testing**: Use `index.html` or `chat-ui.html` for interactive testing

### Dependencies
- **Install**: `pip install -r requirements.txt`
- **Required env**: `.env` file with `GROQ_API_KEY=your_key_here`

## Architecture Overview

### Core Components

**Orchestrator System**: The heart of the application (`orchestrator/orchestrator.py`) manages conversation flow and agent routing. It processes user messages through:
1. Sentiment analysis (via `SentimentAgent`)
2. Anger meter evaluation (`utils/anger_meter.py`)
3. Agent selection based on emotional state
4. Response generation through selected agent

**Agent System**: All agents inherit from `BaseAgent` (`agents/base_agent.py`) and use Groq's Llama 3.1-8B-Instant model. Agent hierarchy:
- **Normal Agent**: Default neutral responses
- **Happy Agents**: Level 1 (pleased), Level 2 (cheerful), Level 3 (ecstatic)
- **Sad Agents**: Level 1 (melancholy), Level 2 (sorrowful), Level 3 (depressed)  
- **Angry Agents**: Level 1 (irritated), Level 2 (agitated), Level 3 (enraged)
- **Sentiment Agent**: Analyzes emotional content of messages
- **Orchestrator Agent**: Makes routing decisions between agents

**Anger Meter System**: Dynamic anger tracking (`utils/anger_meter.py`) that:
- Accumulates anger points based on user messages and detected emotions
- Uses configurable thresholds (irritated: 20pts, agitated: 50pts, enraged: 80pts)
- Applies decay over time and messages
- Handles escalation/de-escalation logic
- Configuration via `anger_config.yaml`

### Key Features

**Conversation Management**: Each conversation has unique ID with persistent history. New conversations trigger orchestrator state reset.

**External Prompts**: All agent personalities defined in `prompts/` directory as markdown files, loaded via `utils/prompt_loader.py`.

**Thinking Tags**: Agents use `<t></t>` tags to show reasoning process in responses.

**State Transitions**: Enforces conversation flow rules (e.g., cannot jump directly from agitated to normal without de-escalation).

**Conversation Termination**: System detects goodbye messages and conversation walkaway scenarios for enraged states.

### API Structure

**Main Endpoints**:
- `POST /chat`: Primary chat interface with sentiment analysis data
- `GET /conversations/{id}`: Retrieve conversation history  
- `DELETE /conversations/{id}`: Clear conversation
- `POST /reset`: Reset orchestrator state and clear all conversations
- `GET /health`: Health check endpoint

**Response Format**: All chat responses include:
- Agent response text
- Agent type used
- Sentiment analysis data
- Orchestrator decision reasoning
- Orchestrator insights and trajectory tracking

### Development Notes

**Agent Development**: When creating new agents, follow the base class pattern and ensure prompts are externalized to `prompts/` directory.

**Testing Strategy**: Use test scripts in `test scripts/` for specific scenarios. Main server must be running (`./startup.sh`) before running test scripts.

**Configuration**: Anger meter behavior is configurable via `anger_config.yaml`. Modify thresholds, decay rates, and bonuses/penalties as needed.

**Debugging**: All agents support thinking tags for visibility into decision-making. Orchestrator provides detailed insights about emotional trajectory and state transitions.