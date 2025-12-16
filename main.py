from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests
import json
import logging # <--- Importamos el megáfono

# Configuración del Megáfono (Logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEDU_LOGGER")

app = FastAPI()

# --- TUS LLAVES ---
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"
WHATSAPP_TOKEN = "EAAWj4hK4vRkBQPezLTchI09ovFjkqSI5P1bz7c5oj9EkjTExZCOkutT8ZAbUihiU2N75fnziAizQSRIDZCQXRdaAh4qRPYlBQQshXLjV4AtFQ8QmssnSkXgYX2QKskxKtLaIr4CcQ3XBUcCGsADEne9t1rCkVncvZC4eNoxOWGZCNMsZC1z2WcRN3wK9oVfvYqihZCSQRbDDMjh7gWVFJDQvmZAnEn2ZBjvJqvrjKTUdRQyy5gYIXRIwCdKVeCI7LvwZC4KCGPv3skgmsQGNSIpPdnk4q9rXCdyhBX1Y87qQZDZD"
PHONE_NUMBER_ID = "880046795195412"
# ------------------

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ WEBHOOK VERIFICADO CORRECTAMENTE")
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token incorrecto")

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()
        
        # USAMOS LOGGER EN LUGAR DE PRINT
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
                        
                        # Responder
                        respuesta = f"🤖 DEDU Activo: Recibí '{text_body}'"
                        send_whatsapp_message(phone_number, respuesta)
                        
                    elif "statuses" in value:
                        logger.info("ℹ️ Cambio de estado (visto/entregado)")

        return {"status": "recibido"}
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO: {str(e)}")
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
    logger.info(f"📤 RESPUESTA DE META: {response.json()}")
