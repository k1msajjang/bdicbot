from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    jwt_secret_key: str
    jwt_algorithm: str ="HS256"
    jwt_expire_minutes: int = 60
    gemini_api_key: str
    upstash_redis_url: str
    upstash_redis_token: str
    allowed_origins: str = ""

    class Config:
        env_file = ".env"

settings = Settings()