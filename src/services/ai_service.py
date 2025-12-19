import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from typing import List, Dict

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class AIService:
    @staticmethod
    def split_content_to_chunks(
        content: str, max_slides_per_chunk: int = 3
    ) -> List[str]:
        """Split content into smaller chunks based on slides"""
        slides = content.split("**Slide")
        chunks = []

        for i in range(0, len(slides), max_slides_per_chunk):
            chunk_slides = slides[i : i + max_slides_per_chunk]
            # Re-add the **Slide prefix
            chunk = "**Slide".join(chunk_slides).strip()
            if chunk:
                chunks.append(chunk)

        return chunks

    @staticmethod
    def generate_questions_batch(
        topic: str, total_count: int, difficulty: str, content_chunks: List[str]
    ) -> List[Dict]:
        """Generate questions in batches from multiple content chunks"""
        all_questions = []

        if not content_chunks:
            # No context, generate all at once
            return AIService.generate_questions(topic, total_count, difficulty, None)

        # Distribute questions across chunks
        questions_per_chunk = max(1, total_count // len(content_chunks))
        remaining = total_count

        for i, chunk in enumerate(content_chunks):
            if remaining <= 0:
                break

            # Last chunk gets remaining questions
            count = (
                remaining
                if i == len(content_chunks) - 1
                else min(questions_per_chunk, remaining)
            )

            try:
                questions = AIService.generate_questions(
                    topic, count, difficulty, chunk
                )
                all_questions.extend(questions)
                remaining -= len(questions)
            except Exception as e:
                print(f"Error generating questions for chunk {i}: {e}")
                continue

        return all_questions[:total_count]  # Ensure exact count

    @staticmethod
    def generate_questions(
        topic: str, count: int, difficulty: str, context: str = None
    ):
        context_section = ""
        if context:
            context_section = f"""
        
        GUNAKAN MATERI BERIKUT SEBAGAI REFERENSI UNTUK MEMBUAT SOAL:
        ---
        {context}
        ---
        """

        prompt = f"""
        Kamu adalah seorang guru yang professional. Buatkan {count} soal kuis tentang topik "{topic}".
        {context_section}
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
