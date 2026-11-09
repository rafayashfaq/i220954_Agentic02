"""
GigSim standalone server runner.
Can be started via: python -m gigsim.server or uvicorn gigsim:app --port 8001
"""
import uvicorn
from gigsim import app

def run(host: str = "127.0.0.1", port: int = 8001):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run()

