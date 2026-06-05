from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    #  Autenticacion
    token: str
    
    # Servidor
    port: int
    debug: bool
    
    # URLs API Auco
    api_auco_url: str
    webhook_url: str
    
    # Parametros de intento
    max_retries: int
    request_timeout:int
    
    # Historial
    historial_max_size: int = 50
    
    # Mapeo de estados AUCO -> destino
    status_mapping: dict[str, str] = {
        "CREATED": "CREATE",
        "REJECTED": "REJECT",
        "FINISH": "FINISH"
    }
    
    model_config = SettingsConfigDict(
        env_file= Path(__file__).parent.parent / ".env",
        env_file_encoding= "utf-8"
    )

settings = Settings()