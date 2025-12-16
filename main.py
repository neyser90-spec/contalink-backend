from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

# Token secreto para conectar con WhatsApp
VERIFY_TOKEN = "SECRETO_CONTALINK_2026"

@app.get("/")
def home():
    return {"message": "ContaLink 360 - Sistema Operativo"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    # Verificación de WhatsApp
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200)

    raise HTTPException(status_code=403, detail="Error de verificacion")

@app.post("/webhook")
async def receive_message(request: Request):
    # Aquí llegan los mensajes

    return {"status": "received"}
