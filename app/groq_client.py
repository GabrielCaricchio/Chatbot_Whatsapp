import logging
from groq import AsyncGroq
from app.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate_response(self, chat_history: list[dict[str, str]], user_message: str) -> str:
        """
        Generates an AI response using the Groq API with conversation context.
        """
        messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        try:
            logger.info(f"Enviando requisição para Groq (modelo: {settings.GROQ_MODEL})...")
            completion = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
            )
            reply = completion.choices[0].message.content
            return reply.strip() if reply else "Desculpe, não consegui formular uma resposta no momento."
        except Exception as e:
            logger.error(f"Erro ao consultar Groq API: {e}", exc_info=True)
            return "Desculpe, ocorreu uma instabilidade ao processar sua mensagem. Tente novamente em instantes."


groq_service = GroqService()
