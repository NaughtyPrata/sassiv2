#!/bin/bash

echo "🚀 Starting Emotional Chatbot API..."
echo "=" * 50

# Aggressive port killing for port 7878
echo "🔪 Aggressively killing processes on port 7878..."

# Method 1: Kill using lsof
echo "  → Using lsof to find and kill processes..."
PIDS=$(lsof -ti:7878)
if [ ! -z "$PIDS" ]; then
    echo "  → Found PIDs: $PIDS"
    echo "$PIDS" | xargs kill -9
    sleep 1
else
    echo "  → No processes found using lsof"
fi

# Method 2: Kill using netstat and grep (backup method)
echo "  → Using netstat as backup method..."
NETSTAT_PIDS=$(netstat -tulpn 2>/dev/null | grep :7878 | awk '{print $7}' | cut -d'/' -f1 | grep -v -)
if [ ! -z "$NETSTAT_PIDS" ]; then
    echo "  → Found additional PIDs via netstat: $NETSTAT_PIDS"
    echo "$NETSTAT_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
fi

# Method 3: Kill any python processes that might be running our app
echo "  → Killing any existing python chatbot processes..."
pkill -f "main.py" 2>/dev/null
pkill -f "uvicorn.*7878" 2>/dev/null
sleep 2

# Final check
echo "  → Final port check..."
if lsof -ti:7878 >/dev/null 2>&1; then
    echo "  ⚠️  Warning: Port 7878 might still be in use"
    echo "  → Attempting one more aggressive kill..."
    lsof -ti:7878 | xargs kill -9 2>/dev/null
    sleep 3
else
    echo "  ✅ Port 7878 is now free"
fi

echo ""
echo "🔧 Setting up environment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OpenAI API key"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, openai, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies missing. Installing..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting FastAPI server on port 7878..."
echo "📍 API will be available at: http://localhost:7878"
echo "📖 API docs will be available at: http://localhost:7878/docs"
echo "🌐 Web UI: Open index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=" * 50

# Start the application
python main.py 