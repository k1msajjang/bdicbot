from fastapi import APIRouter,HTTPException
from app.db.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/master-data", tags=["Master Data"])

def fetch_master_data(table_name : str):
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        logger.error(f"Gagal ambil data dari tabel {table_name}: {e}")
        raise HTTPException(status_code=503, detail="Gagal mengambil data, silahkan coba lagi nanti.")

@router.get("/categories")
def get_categories():
   return  {"data": fetch_master_data("programs"), "message": "Success"}
@router.get("/programs")
def get_programs():
    return {"data": fetch_master_data("programs"), "message": "Success"}

@router.get("/tags")
def get_tags():
    return {"data": fetch_master_data("tags"), "message": "Success"}

@router.get("/roles")
def get_roles():
    return {"data": fetch_master_data("roles"), "message": "Success"}