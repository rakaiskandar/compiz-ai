from mangum import Mangum
from src.main import app

# Vercel serverless function handler
handler = Mangum(app, lifespan="off")
