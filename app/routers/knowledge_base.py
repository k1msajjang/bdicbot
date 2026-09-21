from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.knowledge_base_schemas import CreateKnowledgeBaseRequest, ToggleStatusRequest, UpdateKnowledgeBaseRequest
from app.services.knowledge_base_service import (
    create_knowledge_base_entry, toggle_knowledge_base_status,
    update_knowledge_base_entry, delete_knowledge_base_entry
)
from app.services.bulk_upload_service import parse_upload_file, process_bulk_upload
from app.utils.deps import get_current_user, require_superadmin
from fastapi import HTTPException

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.post("")
def create_entry(payload: CreateKnowledgeBaseRequest, current_user: dict = Depends(get_current_user)):
    new_id = create_knowledge_base_entry(
        judul=payload.judul,
        jawaban=payload.jawaban,
        category_ids=payload.category_ids,
        program_ids=payload.program_ids,
        tag_ids=payload.tag_ids,
        user_id=current_user["user_id"]
    )
    return {"id": new_id, "message": "Entry berhasil dibuat, status masih nonaktif"}


MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB

@router.post("/bulk-upload")
async def bulk_upload_entries(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    content = await file.read(MAX_FILE_SIZE_BYTES + 1)
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran file maksimal 2MB")

    df = parse_upload_file(file.filename, content)
    result = process_bulk_upload(df, current_user["user_id"])
    return result

@router.patch("/{entry_id}/status")
def toggle_status(entry_id: int, payload: ToggleStatusRequest, current_user: dict = Depends(get_current_user)):
    toggle_knowledge_base_status(entry_id, payload.status, current_user["user_id"])
    action_text = "diaktifkan" if payload.status else "dinonaktifkan"
    return {"message": f"Entry berhasil {action_text}"}


@router.put("/{entry_id}")
def update_entry(entry_id: int, payload: UpdateKnowledgeBaseRequest, current_user: dict = Depends(get_current_user)):
    update_knowledge_base_entry(
        entry_id=entry_id, judul=payload.judul, jawaban=payload.jawaban,
        category_ids=payload.category_ids, program_ids=payload.program_ids, tag_ids=payload.tag_ids,
        user_id=current_user["user_id"]
    )
    return {"message": "Entry berhasil diperbarui, status direset ke nonaktif"}


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, current_user: dict = Depends(require_superadmin)):
    delete_knowledge_base_entry(entry_id, current_user["user_id"])
    return {"message": "Entry berhasil dihapus permanen"}