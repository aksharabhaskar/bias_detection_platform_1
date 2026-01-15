import sys
from pathlib import Path

# Add parent directory to path so we can import main
sys.path.append(str(Path(__file__).parent.parent))

from main import app
from mangum import Mangum

# Mangum adapter for AWS Lambda/Vercel
handler = Mangum(app, lifespan="off", api_gateway_base_path="/api")
