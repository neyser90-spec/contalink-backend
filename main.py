from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests
import json
import logging 

# Configuración de los Logs (El Megáfono para ver errores)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEDU_LOGGER")

app = FastAPI()

# --- TUS LLAVES ACTUALIZADAS (16 Diciembre) ---
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"
WHATSAPP_TOKEN = "EAAWj4hK4vRkBQGCHjrQXlTrcRvRLAmwoLBjHJgLBvkv94aDcAtRkOT9qjb5oxT0AOfUwOmCR4sABIZCu8ua4rjxWgTki9md98SH0FcpJ3HI51JIkKqFWVZAcepU0Yvb9lEy9VVzTueAWTl7z06GzkouzwNqTJ7GoHg62LKQm4YXAZBXeUBET5ZCu36gM3gZAsQ2W1shUEJzbCjvYaeCetTZAOqJAtuxBM5qpM7nIMIJIM5RJFlJNqp61Dq1MvJe0SlKvsgHfCvBHpxp9BYSZC1lhynpNg7fvSogugZDZD"
PHONE_NUMBER_ID = "880046795195412"
# ----------------------------------------------

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
    """Recibe mensajes, los imprime y responde"""
    try:
        data = await request.json()
        
        # 1. IMPRIMIR LO QUE LLEGA
        logger.info(f"📨 PAQUETE RECIBIDO: {json.dumps(data)}")
        
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    
                    # ¿Es un mensaje de texto?
                    if "messages" in value:
                        message_data = value["messages"][0]
                        phone_number = message_data["from"]
                        text_body = message_data["text"]["body"]
                        
                        logger.info(f"👤 MENSAJE DE {phone_number}: {text_body}")
                        
                        # 2. RESPONDER AL USUARIO
                        respuesta = f"🤖 DEDU Resucitado: Te leo fuerte y claro. Dijiste: '{text_body}'"
                        send_whatsapp_message(phone_number, respuesta)
                        
                    elif "statuses" in value:
                        logger.info("ℹ️ Aviso de estado (visto/entregado).")

        return {"status": "recibido"}
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO: {str(e)}")
        return {"status": "error"}

def send_whatsapp_message(to_number, message_text):
    """Envía la respuesta a WhatsApp"""
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
    
    # Imprimir si tuvo éxito o error
    logger.info(f"📤 RESPUESTA DE META: {response.json()}")

