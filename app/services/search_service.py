from app.db.supabase_client import supabase
from app.services.embedding_service import generate_embedding

def execute_cari_faq(query: str) -> list[dict]:
    embedding = generate_embedding(query)
    response = supabase.rpc("cari_faq", {
        "query_embedding": embedding,
        "match_count": 3
    }).execute()
    return response.data
