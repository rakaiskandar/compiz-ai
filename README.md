# Compiz AI - Quiz Generation Backend

FastAPI backend service that generates quiz questions using Google Gemini AI.

## Features

- Generate multiple-choice and true/false questions using AI
- Supabase authentication for secure access
- Customizable topic, difficulty, and question count
- CORS enabled for cross-origin requests

## Tech Stack

- FastAPI
- Google Gemini AI (gemini-2.5-flash)
- Supabase (Auth & Database)
- Python 3.13+

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd compiz-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```

5. **Run the server**
   ```bash
   uvicorn src.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Generate Questions
```
POST /ai/generate
```

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "topic": "Python Programming",
  "difficulty": "medium",
  "count": 5
}
```

**Response:**
```json
{
  "generated": 5,
  "data": {
    "questions": [
      {
        "question_type": "MCQ",
        "question_text": "What is Python?",
        "options_json": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "..."
      }
    ]
  }
}
```

## Authentication

Include the Supabase JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Project Structure
```
compiz-ai/
├── src/
│   ├── api/
│   │   └── question.py
│   ├── dto/
│   │   └── question_dto.py
│   ├── middleware/
│   │   └── auth.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── supabase_service.py
│   └── main.py
├── .env
└── requirements.txt
```