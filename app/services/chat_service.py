from fastapi import HTTPException
from app.services.session_service import get_session_history, save_session_history
from app.services.ai_service import get_ai_response
import logging

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 20

def process_chat_message(session_id: str, message: str) -> str:
    try:
        history = get_session_history(session_id)
    except Exception as e:
        logger.error(f"Gagal ambil histori sesi {session_id}: {e}")
        raise HTTPException(status_code=503, detail="Gagal memuat sesi percakapan, coba lagi nanti")

    try:
        reply = get_ai_response(history, message)
    except Exception as e:
        logger.error(f"Gagal proses AI untuk sesi {session_id}: {e}")
        raise HTTPException(status_code=503, detail="Terjadi gangguan pada sistem, coba lagi sebentar lagi")

    history.append({"role": "user", "text": message})
    history.append({"role": "model", "text": reply})
    history = history[-MAX_HISTORY_MESSAGES:]

    try:
        save_session_history(session_id, history)
    except Exception as e:
        logger.error(f"Gagal simpan histori sesi {session_id}: {e}")
        # SENGAJA tidak di-raise — user udah dapet jawaban valid, jangan
        # digagalin gara-gara langkah "simpan histori" doang yang gagal.
        # Konsekuensinya cuma: percakapan berikutnya gak inget konteks ini.

    return reply