import json
from app.db.redis_client import redis

SESSION_TTL_SECONDS = 30 * 60

def get_session_history(session_id: str) -> list[dict]:
    data = redis.get(f"session: {session_id}")
    if data is None:
        return []
    return json.loads(data)

def save_session_history(session_id: str, history: list[dict]) -> None:
    redis.set(f"session: {session_id}", json.dumps(history, ex=SESSION_TTL_SECONDS))