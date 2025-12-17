from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests
import json
import logging

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEDU_LOGGER")

app = FastAPI()

# --- TUS DATOS (Verificados) ---
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"
# Token Nuevo (Terminación sfUZD)
WHATSAPP_TOKEN = "EAAWj4hK4vRkBQAgxLZCptJ8ZBJw7SJ5ZBM3Fx52ZA2KvFx1xATTYxd11Cngpc4Qoje1xh8OfOGZCG1VYg1UWhNKv3JDKT84zrYtk47hfZCv9YqWqzrg6xrq2jLvafzkmOcfNCxufwxLftLjV309tZANY6iqF230UHXgItmsqQ0U3MuWpgjYZAyT0TEroOzbtyMVgvFCOmS9a0xQxyzLTwiUPYMT1ZBPW9eftS6bLlAOFyXLWv6gcZCVZCqxwjqLlk9ZA8b6JB1KvmTMcBRO3KRTPwB0UGlly4kjBxyc8sfUZD"
PHONE_NUMBER_ID = "880046795195412"
# -------------------------------

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verifica el token secreto con Facebook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ WEBHOOK VERIFICADO")
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token incorrecto")

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()
        logger.info(f"📨 PAQUETE RECIBIDO: {json.dumps(data)}")
        
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        message_data = value["messages"][0]
                        phone_number = message_data["from"]
                        text_body = message_data["text"]["body"]
                        
                        logger.info(f"👤 MENSAJE DE {phone_number}: {text_body}")
                        
                        # RESPONDER
                        respuesta = f"🤖 DEDU RESPONDE: Recibido '{text_body}'"
                        send_whatsapp_message(phone_number, respuesta)

        return {"status": "recibido"}
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        return {"status": "error"}

def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, json=data, headers=headers)
    logger.info(f"📤 RESPUESTA META: {response.json()}")
