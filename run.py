"""
NexusSupply AI - Application Entrypoint
Run this script to launch the unified FastAPI backend + interactive UI:
    python run.py
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    port = int(os.environ.get("APP_PORT", 8000))
    print("\n" + "=" * 65)
    print(" 🚀 NexusSupply AI | IBM BoB Supply Chain Assistant & Fleet Optimizer")
    print(" 👥 Team: Orion Squad  |  Track: AI")
    print(f" 🌐 Dashboard available at: http://localhost:{port}")
    print(f" 📚 API Documentation at:  http://localhost:{port}/docs")
    print("=" * 65 + "\n")
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=port, reload=True)
