from google import genai
from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

def generate_embedding(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={"output_dimensionality": 768}
    )
    return result.embeddings[0].values