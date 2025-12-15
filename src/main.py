from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import question
import uvicorn

app = FastAPI(title="Compiz AI")

app.include_router(question.router)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI backend running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
