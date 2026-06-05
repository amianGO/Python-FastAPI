import asyncio
import logging

import httpx
from app.config import settings

# Consola
logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=settings.request_timeout,
                headers={
                    "Authorization": f"{settings.token}",
                    "Accept": "application/json"
                },
            )
        return self._client

    async def _retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exception = None
        for attemp in range(settings.max_retries):
            try:
                client = await self.get_client()
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exception = exc
                logger.warning(
                    "Intento %d%d fallo para %s %s: %s",
                    attemp + 1, settings.max_retries, method, url, exc
                )
                if attemp < settings.max_retries - 1:
                    wait = 2 ** attemp
                    await asyncio.sleep(wait)
        raise last_exception # type: ignore[misc]
    
    async def get_document(self, code: str) -> dict:
        url = f"{settings.api_auco_url}?code={code}"
        response = await self._retry("GET", url)
        return response.json()
    
    async def post_webhook(self, code: str, status: str) -> dict:
        payload = {"code": code, "status": status}
        response = await self._retry("POST",settings.webhook_url,json=payload)
        return response.json()
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

api_client = APIClient()
