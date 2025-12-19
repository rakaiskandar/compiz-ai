from fastapi import APIRouter, Depends
from src.dto.question_dto import GenerateRequest
from src.services.ai_service import AIService
from src.services.supabase_service import SupabaseService
from src.middleware.auth import verify_token

router = APIRouter(prefix="/ai")


@router.post("/generate")
async def generate_questions(req: GenerateRequest, user=Depends(verify_token)):
    context = None

    # Auto-find course by topic
    course_id = SupabaseService.find_course_by_topic(req.topic)

    if course_id:
        print(f"✅ Found course for topic '{req.topic}': {course_id}")

        # Get course contents directly from Supabase (no embeddings needed)
        contents = SupabaseService.get_course_contents_by_topic(course_id, req.topic)

        if contents:
            print(f"\n=== Found {len(contents)} relevant content slides ===")
            # Combine all content as context
            context = "\n\n".join(
                [
                    f"**Slide {c['slide_number']}**\n{c['content']}"
                    for c in contents
                    if c.get("content")
                ]
            )
        else:
            print("\n=== No content found for this course ===")
    else:
        print(
            f"ℹ️ No matching course found for topic '{req.topic}', generating without context"
        )

    # Generate questions with chunked context for better token efficiency
    if context:
        chunks = AIService.split_content_to_chunks(context, max_slides_per_chunk=3)
        print(f"📦 Split context into {len(chunks)} chunks")
        questions = AIService.generate_questions_batch(
            req.topic, req.count, req.difficulty, chunks
        )
    else:
        # No context found, generate without context
        questions = AIService.generate_questions(
            req.topic, req.count, req.difficulty, None
        )
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
