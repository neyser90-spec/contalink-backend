from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests
import json 

app = FastAPI()

# --- TUS LLAVES (LLÉNALAS OTRA VEZ) ---
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"
WHATSAPP_TOKEN = "EAAG..."  # <--- ¡EAAWj4hK4vRkBQPezLTchI09ovFjkqSI5P1bz7c5oj9EkjTExZCOkutT8ZAbUihiU2N75fnziAizQSRIDZCQXRdaAh4qRPYlBQQshXLjV4AtFQ8QmssnSkXgYX2QKskxKtLaIr4CcQ3XBUcCGsADEne9t1rCkVncvZC4eNoxOWGZCNMsZC1z2WcRN3wK9oVfvYqihZCSQRbDDMjh7gWVFJDQvmZAnEn2ZBjvJqvrjKTUdRQyy5gYIXRIwCdKVeCI7LvwZC4KCGPv3skgmsQGNSIpPdnk4q9rXCdyhBX1Y87qQZDZD!
PHONE_NUMBER_ID = "880..."  # <--- ¡880046795195412!
# --------------------------------------

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token incorrecto")

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()
        
        # 1. IMPRIMIR LO QUE LLEGA (CÁMARA DE SEGURIDAD)
        print("📨 PAQUETE RECIBIDO:", json.dumps(data))
        
        # Navegamos el JSON con cuidado
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    
                    # ¿Es un mensaje real?
                    if "messages" in value:
                        message_data = value["messages"][0]
                        phone_number = message_data["from"]
                        text_body = message_data["text"]["body"]
                        
                        print(f"👤 MENSAJE DETECTADO de {phone_number}: {text_body}")
                        
                        # Intentar responder
                        send_whatsapp_message(phone_number, f"🤖 DEDU te escucha: {text_body}")
                    
                    # ¿Es solo un aviso de visto/entregado?
                    elif "statuses" in value:
                        print("ℹ️ Solo es un aviso de estado (visto/entregado). Ignorando.")

        return {"status": "recibido"}
    except Exception as e:
        print(f"❌ ERROR EN EL CÓDIGO: {str(e)}")
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
    print("📤 INTENTO DE RESPUESTA:", response.json())

