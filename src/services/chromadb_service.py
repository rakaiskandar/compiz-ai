import chromadb
import os
from pathlib import Path

# Setup ChromaDB client
CHROMA_PATH = os.path.join(Path(__file__).parent.parent.parent, "chroma_data")
os.makedirs(CHROMA_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_PATH)

class ChromaService:
    COLLECTION_NAME = "course_contents"

    @staticmethod
    def get_or_create_collection():
        """Get or create the ChromaDB collection"""
        try:
            collection = client.get_or_create_collection(
                name=ChromaService.COLLECTION_NAME,
                metadata={
                    "description": "Course content embeddings for quiz generation"
                },
            )
            return collection
        except Exception as e:
            print(f"Error getting/creating collection: {e}")
            return None

    @staticmethod
    def store_course_content(
        course_id: str,
        content_id: str,
        slide_number: int,
        content: str,
        embedding: list,
    ):
        """Store course content with embedding in ChromaDB"""
        try:
            collection = ChromaService.get_or_create_collection()
            if not collection:
                return False

            # Create unique ID for this content
            doc_id = f"{course_id}_{content_id}_{slide_number}"

            # Store in ChromaDB
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[
                    {
                        "course_id": course_id,
                        "content_id": content_id,
                        "slide_number": slide_number,
                    }
                ],
                ids=[doc_id],
            )
            return True
        except Exception as e:
            print(f"Error storing content in ChromaDB: {e}")
            return False

    @staticmethod
    def search_similar_content(
        course_id: str, query_embedding: list, n_results: int = 5
    ):
        """Search for similar content in a specific course"""
        try:
            collection = ChromaService.get_or_create_collection()
            if not collection:
                return []

            # Query ChromaDB with course_id filter
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"course_id": course_id},
            )

            # Format results
            if results and results["documents"]:
                formatted_results = []
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append(
                        {
                            "content": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i]
                            if "distances" in results
                            else None,
                        }
                    )
                return formatted_results
            return []
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []

    @staticmethod
    def check_course_exists(course_id: str):
        """Check if a course has any stored embeddings"""
        try:
            collection = ChromaService.get_or_create_collection()
            if not collection:
                return False

            # Try to get one document with this course_id
            results = collection.get(where={"course_id": course_id}, limit=1)
            return len(results["ids"]) > 0
        except Exception as e:
            print(f"Error checking course existence: {e}")
            return False

    @staticmethod
    def delete_course_embeddings(course_id: str):
        """Delete all embeddings for a specific course"""
        try:
            collection = ChromaService.get_or_create_collection()
            if not collection:
                return False

            # Get all IDs for this course
            results = collection.get(where={"course_id": course_id})

            if results["ids"]:
                collection.delete(ids=results["ids"])
                return True
            return False
        except Exception as e:
            print(f"Error deleting course embeddings: {e}")
            return False

    @staticmethod
    def get_collection_stats():
        """Get statistics about the collection"""
        try:
            collection = ChromaService.get_or_create_collection()
            if not collection:
                return None

            return {"total_documents": collection.count(), "name": collection.name}
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return None
