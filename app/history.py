from collections import OrderedDict
from datetime import datetime

from app.config import settings

class HistoryStore:
    def __init__(self):
        self._store: OrderedDict[str, dict] = OrderedDict()
    
    def add(self, entry: dict) -> None:
        now = datetime.now()
        key = f"{entry.get('codigo', 'unknow')}_{now.timestamp()}"
        
        record = {
            "codigo": entry.get("codigo", ""),
            "accion": entry.get("accion", ""),
            "api_status": entry.get("api_status"),
            "mapped_status": entry.get("mapped_status"),
            "webhook_sent": entry.get("webhook_sent", False),
            "error": entry.get("error"),
            "timestamp": now.isoformat(),
            "hora": now.strftime("%H:%M:%S"),
        }
        self._store[key] = record
        
        while len(self._store) > settings.historial_max_size:
            self._store.popitem(last=False)
    
    def get_all(self) -> list[dict]:
        return list(reversed(self._store.values()))
    
    def get_last_by_code(self, code: str) -> dict | None:
        for record in reversed(self._store.values()):
            if record['codigo'] == code:
                return record
        return None
    
    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

history_store = HistoryStore()