from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class StatusEnum(str, Enum):
    created = "CREATED",
    rejected = "REJECTED",
    finish = "FINISH"

class DocumentRequest(BaseModel):
    code: str

class ReprocessRequest(BaseModel):
    code: str
    refresh: bool = True
    
class DocumentResponse(BaseModel):
    sucess: bool
    code: str
    data: dict | None = None
    
class ProcessResult(BaseModel):
    code: str
    api_get_status: str | None = None
    mapped_status: str | None = None
    webhook_sent: bool = False
    webhook_response: dict | None = None
    error: str | None = None
    
class WebhookPayload(BaseModel):
    code: str
    status: str
    
class HistoryEntry(BaseModel):
    code: str
    accion: str
    api_status: str | None = None
    mapped_status: str | None = None
    webhook_sent: bool = False
    error: str | None = None
    timestamp: str
    hora: str