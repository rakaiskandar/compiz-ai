import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class EmbeddingService:
    @staticmethod
    def generate_embedding(text: str):
        """Generate embedding vector using Gemini API (free tier)

        Args:
            text: Text content to convert to embedding

        Returns:
            List of floats representing the embedding vector (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    @staticmethod
    def generate_query_embedding(text: str):
        """Generate embedding for search query

        Args:
            text: Query text to convert to embedding

        Returns:
            List of floats representing the query embedding vector (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None
