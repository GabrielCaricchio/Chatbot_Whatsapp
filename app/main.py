import logging
from collections import OrderedDict
from fastapi import FastAPI, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.groq_client import groq_service
from app.waha_client import waha_client
from app.memory import memory

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("whatsapp_bot")

app = FastAPI(
    title="WhatsApp Chatbot Groq",
    version="1.0.0",
    description="Chatbot integrado ao WhatsApp via WAHA e alimentado por Groq AI"
)

# Deduplication cache (stores up to 1000 message IDs)
class MessageDeduplicator:
    def __init__(self, max_size: int = 1000):
        self.seen = OrderedDict()
        self.max_size = max_size

    def is_duplicate(self, message_id: str) -> bool:
        if not message_id:
            return False
        if message_id in self.seen:
            return True
        self.seen[message_id] = True
        if len(self.seen) > self.max_size:
            self.seen.popitem(last=False)
        return False


deduplicator = MessageDeduplicator()


async def process_incoming_message(chat_id: str, message_id: str, message_text: str, session: str):
    """
    Background worker that handles Groq AI completion and sends response back to WhatsApp.
    """
    try:
        logger.info(f"Processando mensagem de {chat_id} (sessão: {session}): '{message_text}'")

        # Mark message as seen
        await waha_client.send_seen(chat_id=chat_id, message_id=message_id, session=session)

        # Show typing indicator in WhatsApp
        await waha_client.start_typing(chat_id=chat_id, session=session)

        # Get existing conversation context
        history = memory.get_messages(chat_id=chat_id)

        # Call Groq AI
        ai_reply = await groq_service.generate_response(chat_history=history, user_message=message_text)

        # Update memory
        memory.add_user_message(chat_id=chat_id, content=message_text)
        memory.add_assistant_message(chat_id=chat_id, content=ai_reply)

        # Stop typing indicator
        await waha_client.stop_typing(chat_id=chat_id, session=session)

        # Send reply to user via WAHA
        success = await waha_client.send_text(chat_id=chat_id, text=ai_reply, session=session)
        if success:
            logger.info(f"Resposta enviada com sucesso para {chat_id} via sessão {session}")
        else:
            logger.warning(
                f"Mensagem gerada com sucesso pela IA, mas não pôde ser entregue ao WAHA para {chat_id}. "
                f"Verifique se a sessão '{session}' está no status WORKING."
            )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem para {chat_id}: {e}", exc_info=True)
        await waha_client.stop_typing(chat_id=chat_id, session=session)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "WhatsApp Groq Chatbot",
        "model": settings.GROQ_MODEL,
        "waha_url": settings.WAHA_API_URL
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def waha_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint receiving events from WAHA (WhatsApp HTTP API).
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid JSON"})

    event = data.get("event")
    session = data.get("session") or settings.WAHA_SESSION
    payload = data.get("payload", {})

    logger.debug(f"Webhook recebido - Sessão: {session}, Evento: {event}")

    # Process only incoming message events
    if event not in ("message", "message.any"):
        return {"status": "ignored", "reason": f"Event '{event}' not handled"}

    from_me = payload.get("fromMe", False)
    if from_me:
        # Ignore messages sent by the bot/self
        return {"status": "ignored", "reason": "Message from self (fromMe=True)"}

    chat_id = payload.get("from") or payload.get("chatId")
    if not chat_id:
        return {"status": "ignored", "reason": "No chat_id found in payload"}

    # Ignore WhatsApp status broadcast
    if "status@broadcast" in chat_id or "broadcast" in chat_id:
        return {"status": "ignored", "reason": "Status broadcast ignored"}

    # Ignore group messages if configured
    if settings.IGNORE_GROUPS and (chat_id.endswith("@g.us") or "@g.us" in chat_id):
        logger.info(f"Mensagem de grupo ignorada: {chat_id}")
        return {"status": "ignored", "reason": "Group messages are disabled"}

    message_id = payload.get("id")
    if message_id and deduplicator.is_duplicate(message_id):
        logger.info(f"Mensagem duplicada ignorada: {message_id}")
        return {"status": "ignored", "reason": "Duplicate message"}

    message_text = payload.get("body", "").strip()
    if not message_text:
        # If message has no text (e.g. sticker/image without caption)
        if payload.get("hasMedia"):
            message_text = "Recebi uma mídia/arquivo. Por favor, envie texto para conversarmos!"
            background_tasks.add_task(waha_client.send_text, chat_id, message_text, session)
            return {"status": "media_not_supported_notified"}
        return {"status": "ignored", "reason": "Empty message body"}

    # Dispatch to background task to respond quickly to webhook
    background_tasks.add_task(
        process_incoming_message,
        chat_id=chat_id,
        message_id=message_id,
        message_text=message_text,
        session=session
    )

    return {"status": "processing"}
