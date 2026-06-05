import logging

from app.config import settings
from app.api_client import api_client

logger = logging.getLogger(__name__)

def map_status(api_status: str | None) -> str:
    if api_status is None:
        return "ERROR"
    return settings.status_mapping.get(api_status, "ERROR")

async def process_document(code: str, refresh: bool = True) -> dict:
    if not code or not code.strip():
        return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": "El codigo es requerido"
        }
    code = code.strip()
    
    if refresh:
        try:
            data = await api_client.get_document(code)
            api_status = data.get("status")
        except Exception as exc:
            return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": f"API GET fallo despues de {settings.max_retries} intentos {exc}"
            }
        if not api_status:
            return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": "API GET no retorno campo 'status'",
            }
    else: 
        api_status = None
    
    mapped_status = map_status(api_status)
    
    result = {
        "code": code,
        "api_get_status": api_status,
        "mapped_status": mapped_status,
        "webhook_sent": False,
        "webhook_response": None,
        "error": None
    }
    
    return result

async def reprocess_document(code: str, refresh: bool = True) -> dict:
    if not code or not code.strip():
        return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": "El codigo es requerido"
        }
    code = code.strip()
    api_status = None
    
    if refresh:
        try:
            data = await api_client.get_document(code)
            api_status = data.get("status")
        except Exception as exc:
            return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": f"API GET fallo despues de {settings.max_retries} intentos {exc}"
            }
        if not api_status:
            return {
            "code": code,
            "api_get_status": None,
            "mapped_status": None,
            "webhook_sent": False,
            "webhook_response": None,
            "error": "API GET no retorno campo 'status'",
            }
    mapped_status = map_status(api_status)
    webhook_sent = False
    webhook_response = None
    error = None
    
    if mapped_status == "ERROR" and api_status is not None:
        error = f"Estado desconocido: {api_status}"
    elif mapped_status == "ERROR":
        error = "No se pudo obtener el estado del documento"
    else:
        try:
            webhook_response = await api_client.post_webhook(code, mapped_status)
            webhook_sent = True
        except Exception as exc:
            error = f"Webhook fallo: {exc}"
    
    return {
        "code": code,
        "api_get_status": api_status,
        "mapped_status": mapped_status,
        "webhook_sent": webhook_sent,
        "webhook_response": webhook_response,
        "error": error
    }