import logging
import httpx
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WahaClient:
    def __init__(self):
        self.base_url = settings.WAHA_API_URL.rstrip("/")
        self.default_session = settings.WAHA_SESSION
        self.headers = {}
        if settings.WAHA_API_KEY:
            self.headers["X-Api-Key"] = settings.WAHA_API_KEY

    async def send_text(self, chat_id: str, text: str, session: Optional[str] = None) -> bool:
        """
        Sends a plain text message to a WhatsApp chat via WAHA API.
        """
        url = f"{self.base_url}/api/sendText"
        session_name = session or self.default_session
        payload = {
            "chatId": chat_id,
            "text": text,
            "session": session_name,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
                response = await client.post(url, json=payload)
                if response.status_code in (200, 201):
                    logger.info(f"Mensagem enviada com sucesso para {chat_id} (sessão: {session_name})")
                    return True
                else:
                    logger.error(
                        f"Falha ao enviar mensagem via WAHA. Status: {response.status_code}, Resposta: {response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Erro ao conectar com WAHA API ({url}): {e}")
            return False

    async def start_typing(self, chat_id: str, session: Optional[str] = None):
        """
        Sets the bot status to 'typing...' in WhatsApp chat.
        """
        url = f"{self.base_url}/api/startTyping"
        payload = {"chatId": chat_id, "session": session or self.default_session}
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=self.headers) as client:
                await client.post(url, json=payload)
        except Exception as e:
            logger.debug(f"Erro ao disparar startTyping para {chat_id}: {e}")

    async def stop_typing(self, chat_id: str, session: Optional[str] = None):
        """
        Stops the 'typing...' status.
        """
        url = f"{self.base_url}/api/stopTyping"
        payload = {"chatId": chat_id, "session": session or self.default_session}
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=self.headers) as client:
                await client.post(url, json=payload)
        except Exception as e:
            logger.debug(f"Erro ao disparar stopTyping para {chat_id}: {e}")

    async def send_seen(self, chat_id: str, message_id: Optional[str] = None, session: Optional[str] = None):
        """
        Marks incoming message as seen / read.
        """
        url = f"{self.base_url}/api/sendSeen"
        payload = {"chatId": chat_id, "session": session or self.default_session}
        if message_id:
            payload["messageId"] = message_id
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=self.headers) as client:
                await client.post(url, json=payload)
        except Exception as e:
            logger.debug(f"Erro ao marcar mensagem como vista para {chat_id}: {e}")


waha_client = WahaClient()
