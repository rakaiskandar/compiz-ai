from fastapi import APIRouter, Depends
from src.dto.question_dto import GenerateRequest, ProcessCourseRequest
from src.services.ai_service import AIService
from src.services.embedding_service import EmbeddingService
from src.services.chromadb_service import ChromaService
from src.services.supabase_service import SupabaseService
from src.middleware.auth import verify_token

router = APIRouter(prefix="/ai")


@router.post("/process-course")
async def process_course(req: ProcessCourseRequest, user=Depends(verify_token)):
    """Process course contents and store embeddings in ChromaDB (one-time per course)"""

    # Check if already processed
    if ChromaService.check_course_exists(req.course_id):
        return {
            "message": "Course already processed",
            "course_id": req.course_id,
            "note": "Use DELETE /ai/course/{course_id} to reprocess",
        }

    # Get all course contents from Supabase
    contents = SupabaseService.get_course_contents(req.course_id)

    if not contents:
        return {
            "message": "No contents found for this course",
            "course_id": req.course_id,
            "contents_found": 0,
        }

    processed_count = 0

    for content in contents:
        if not content.get("content"):
            continue

        # Generate embedding for the content
        embedding = EmbeddingService.generate_embedding(content["content"])

        if embedding:
            # Store in ChromaDB
            success = ChromaService.store_course_content(
                course_id=req.course_id,
                content_id=content["id"],
                slide_number=content["slide_number"],
                content=content["content"],
                embedding=embedding,
            )

            if success:
                processed_count += 1
                print(f"Processed slide {content['slide_number']}")

    return {
        "message": "Course processed successfully",
        "course_id": req.course_id,
        "slides_processed": processed_count,
        "total_slides": len(contents),
    }


@router.delete("/course/{course_id}")
async def delete_course_embeddings(course_id: str, user=Depends(verify_token)):
    """Delete all embeddings for a course"""
    success = ChromaService.delete_course_embeddings(course_id)

    if success:
        return {
            "message": "Course embeddings deleted successfully",
            "course_id": course_id,
        }
    return {"message": "No embeddings found for this course", "course_id": course_id}


@router.get("/stats")
async def get_stats(user=Depends(verify_token)):
    """Get ChromaDB collection statistics"""
    stats = ChromaService.get_collection_stats()
    return stats if stats else {"message": "Unable to fetch stats"}


@router.post("/generate")
async def generate_questions(req: GenerateRequest, user=Depends(verify_token)):
    context = None

    # Auto-find course by topic
    course_id = SupabaseService.find_course_by_topic(req.topic)

    if course_id:
        print(f"✅ Found course for topic '{req.topic}': {course_id}")

        # Check if course is processed in ChromaDB
        if ChromaService.check_course_exists(course_id):
            # Generate query embedding
            query_embedding = EmbeddingService.generate_query_embedding(req.topic)

            if query_embedding:
                # Search for relevant content in ChromaDB
                similar_contents = ChromaService.search_similar_content(
                    course_id=course_id,
                    query_embedding=query_embedding,
                    n_results=5,
                )

                if similar_contents:
                    print(
                        f"\n=== Found {len(similar_contents)} relevant content chunks ==="
                    )
                    # Sort by slide number
                    similar_contents.sort(key=lambda x: x["metadata"]["slide_number"])
                    context = "\n\n".join(
                        [item["content"] for item in similar_contents]
                    )
                else:
                    print("\n=== No relevant content found ===")
        else:
            print("⚠️ Course found but not processed in ChromaDB yet")
    else:
        print(
            f"ℹ️ No matching course found for topic '{req.topic}', generating without context"
        )

    # Generate questions with or without context
    questions = AIService.generate_questions(
        req.topic, req.count, req.difficulty, context
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
