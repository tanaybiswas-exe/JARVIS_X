import asyncio
import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.ai.provider import OpenAICompatibleProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.ws.connection_manager import WebSocketHub

app = FastAPI(title="JARVIS-X Core Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.JARVIS_CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = OpenAICompatibleProvider(
    api_key=settings.JARVIS_AI_API_KEY,
    base_url=settings.JARVIS_AI_API_BASE,
    model=settings.JARVIS_AI_MODEL
)
orchestrator = AIOrchestrator(provider=provider)
ws_hub = WebSocketHub()

@app.on_event("startup")
async def start_telemetry_loop():
    async def poll_system():
        while True:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            await ws_hub.broadcast({
                "type": "telemetry",
                "cpu": cpu,
                "ram": mem,
                "status": "NOMINAL" if cpu < 80 else "HIGH LOAD"
            })
            await asyncio.sleep(2.0)
    asyncio.create_task(poll_system())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_hub.connect(websocket)
    try:
        while True:
            raw_msg = await websocket.receive_text()
            import json
            data = json.loads(raw_msg)
            
            if data.get("type") == "user_command":
                user_prompt = data.get("text", "")
                
                async def notify_client(ev: dict):
                    await websocket.send_json(ev)

                response_text = await orchestrator.process_user_turn(user_prompt, notify_client)
                await websocket.send_json({
                    "type": "ai_response",
                    "text": response_text
                })
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket)
    except Exception as ex:
        await websocket.send_json({"type": "error", "message": str(ex)})
        ws_hub.disconnect(websocket)