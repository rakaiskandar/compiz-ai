import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class AIService:
    @staticmethod
    def generate_questions(topic: str, count: int, difficulty: str):
        prompt = f"""
        Kamu adalah seorang guru yang professional. Buatkan {count} soal kuis tentang topik "{topic}".
        
        Ketentuan:
        - Jenis soal: Pilihan Ganda (MCQ) dan Benar/Salah (True/False).
        - Tingkat kesulitan: {difficulty}.
        - Bahasa: Gunakan Bahasa Indonesia yang baku dan benar.
        - Format Output: HANYA berikan array JSON (tanpa teks pembuka/penutup lain):

        [
        {{
            "type": "mcq",
            "question": "Tulis pertanyaan di sini",
            "options": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
            "correct_answer": "Isi teks jawaban yang benar",
            "explanation": "Penjelasan jawaban"
        }},
        {{
            "type": "true_false",
            "question": "Tulis pernyataan di sini",
            "correct_answer": "True", 
            "explanation": "Penjelasan jawaban"
        }}
        ]
        """

        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)

        # Extract text and clean markdown code blocks
        text = response.text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]  # Remove ```json
        elif text.startswith("```"):
            text = text[3:]  # Remove ```

        if text.endswith("```"):
            text = text[:-3]  # Remove closing ```

        text = text.strip()

        parsed_json = json.loads(text)

        return parsed_json
