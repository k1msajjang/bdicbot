from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.config import settings
from app.routers import master_data, auth, knowledge_base, chat,users
import logging


logger = logging.getLogger(__name__)


app = FastAPI(title="Chatbot BDI Denpasar")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins],
    allow_methods=["GET","POST","PUT","PATCH","DELETE"]
)
app.include_router(master_data.router)
app.include_router(auth.router)
app.include_router(knowledge_base.router)
app.include_router(chat.router)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail":"Terlalu banyak permintaan, coba lagi nanti."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Input tidak valid"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error di {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Terjadi kesalahan pada server. Silahkan coba lagi nanti."})

@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(users.router)