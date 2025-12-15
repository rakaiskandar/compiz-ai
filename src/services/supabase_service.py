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
        return supabase.table("simulation_questions").select("*").eq("id", qid).execute()
