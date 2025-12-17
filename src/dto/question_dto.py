from pydantic import BaseModel


class GenerateRequest(BaseModel):
    topic: str
    count: int
    difficulty: str


class ProcessCourseRequest(BaseModel):
    course_id: str


class Question(BaseModel):
    type: str
    question: str
    options: list | None
    correct_answer: str
    explanation: str
