from fastapi import APIRouter, Depends
from src.dto.question_dto import GenerateRequest
from src.services.ai_service import AIService
from src.middleware.auth import verify_token

router = APIRouter(prefix="/ai")

@router.post("/generate")
async def generate_questions(req: GenerateRequest, user=Depends(verify_token)):
    questions = AIService.generate_questions(req.topic, req.count, req.difficulty)
    data = []

    for q in questions:
        record = {
            "question_type": q["type"],
            "question_text": q["question"],
            "options_json": q.get("options"),
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
        }
        data.append(record)

    return {"generated": len(data), "data": {"questions": data}}
