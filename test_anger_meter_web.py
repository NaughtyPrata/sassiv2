#!/usr/bin/env python3
"""
Quick test script to start the server and test anger meter functionality
Run this, then open index.html in your browser to test the anger meter visually
"""

import subprocess
import sys
import time
import os

def main():
    print("🔥 Starting Anger Meter Web Test 🔥")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run from the project root directory.")
        sys.exit(1)
    
    print("📋 Test Messages to Try:")
    print("1. 'Hello, how are you?' (should show normal, anger decay)")
    print("2. 'This is annoying' (should start building anger points)")
    print("3. 'I'm getting frustrated!' (should increase anger)")
    print("4. 'This is fucking stupid!' (should add vulgar language bonus)")
    print("5. 'I'M SO DAMN ANGRY!!!' (should trigger higher anger levels)")
    print("6. 'Sorry, I didn't mean that' (should reduce anger with apology)")
    print("7. 'Thank you for your patience' (should further reduce with calm language)")
    print()
    
    print("🚀 Starting server...")
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give the server time to start
        time.sleep(2)
        
        print("✅ Server started successfully!")
        print("🌐 Open index.html in your browser to test the anger meter")
        print("📊 Watch the anger meter bar and points change as you send messages")
        print()
        print("🔧 To fine-tune anger behavior, edit anger_config.yaml")
        print("⚠️  Press Ctrl+C to stop the server")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 