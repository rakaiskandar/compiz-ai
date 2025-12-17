from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class SupabaseService:
    @staticmethod
    def insert_question(question):
        return supabase.table("simulation_questions").insert(question).execute()

    @staticmethod
    def get_question_by_id(qid):
        return (
            supabase.table("simulation_questions").select("*").eq("id", qid).execute()
        )

    @staticmethod
    def find_course_by_topic(topic: str):
        """Find course by matching topic with course title"""
        try:
            # Try exact match first
            response = (
                supabase.table("courses_contents")
                .select("id, title")
                .ilike("title", f"%{topic}%")
                .limit(1)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]["id"]
            return None
        except Exception as e:
            print(f"Error finding course by topic: {e}")
            return None

    @staticmethod
    def get_course_contents(course_id: str):
        """Get all content slides for a course"""
        try:
            response = (
                supabase.table("course_contents")
                .select("*")
                .eq("course_id", course_id)
                .order("slide_number")
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching course contents: {e}")
            return []
