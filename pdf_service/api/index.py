import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app import app

# Vercel serverless handler
handler = app
