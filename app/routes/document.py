import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models import DocumentRequest, ReprocessRequest
from app.webhook_service import process_document, reprocess_document
from app.history import history_store
from app.api_client import api_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def serve_frontend():
    return FileResponse("app/static/index.html")

@router.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "API Integracion AUCO"}

@router.get("/api/historial")
async def get_historual():
    return {"historial": history_store.get_all()}

@router.delete("/api/historial")
async def clear_historial():
    count = history_store.clear()
    return {
        "succes": True,
        "message": f"Historial limpiado. Se eliminaron {count} registros",
        "registros_eliminados": count
    }


@router.get("/api/document/{code}")
async def get_document(code: str):
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="El codigo es requerido")
    
    try:
        data = await api_client.get_document(code)
        return {"sucess": True, "code": code, "data": data}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar documento: {exc}",
        )
        

@router.post("/api/reprocess")
async def reprocess(request: ReprocessRequest):
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="El codigo es requerido")
    
    if not request.refresh:
        last = history_store.get_last_by_code(request.code)
        if last and last.get("api_status"):
            result = await reprocess_document(request.code, refresh=False)
        else:
            result = await reprocess_document(request.code, refresh=True)
    else:
        result = await reprocess_document(request.code, refresh=True)
    
    accion = "Reprocesado" if not result["webhook_sent"] else "webhook Enviado"
    
    history_store.add({
        "codigo": result["code"],
        "accion": accion,
        "api_status": result["api_get_status"],
        "mapped_status": result["mapped_status"],
        "webhook_sent": result["webhook_sent"],
        "error": result["error"],
    })
    
    if result["error"] and not result["webhook_sent"]:
        if result["error"].startswith("Estado desconocido") or result["error"].startswith("No se pudo"):
            raise HTTPException(status_code=500, detail=result["error"])
    
    return result