from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests

app = FastAPI()

# --- TUS LLAVES (CÁMBIALAS) ---
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"
WHATSAPP_TOKEN = "PEGA_AQUI_TU_TOKEN_LARGO_DE_FACEBOOK"
PHONE_NUMBER_ID = "PEGA_AQUI_TU_ID_DE_TELEFONO"
# ------------------------------

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verifica que Facebook sea quien nos toca la puerta"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token incorrecto")

@app.post("/webhook")
async def receive_message(request: Request):
    """Recibe mensajes y responde"""
    try:
        data = await request.json()
        
        # Revisamos si hay un mensaje real
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            phone_number = message_data["from"] # El número del cliente
            text_body = message_data["text"]["body"] # Lo que escribió
            
            # --- LÓGICA DE RESPUESTA ---
            respuesta = f"🤖 Hola, soy DEDU. Recibí tu mensaje: '{text_body}'"
            send_whatsapp_message(phone_number, respuesta)
            
        return {"status": "recibido"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def send_whatsapp_message(to_number, message_text):
    """Función para enviar el mensaje a WhatsApp"""
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
    return response.json()

