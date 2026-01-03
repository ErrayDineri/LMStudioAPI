from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes.health import router as health_router
from app.routes.models import router as models_router
from app.routes.chat import router as chat_router
from app.routes.help import router as help_router

settings = get_settings()

app = FastAPI(title="LM Studio FastAPI Service", version="0.1.0")

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(models_router)
app.include_router(chat_router)
app.include_router(help_router)

@app.get("/")
async def root():
    return {"message": "LM Studio FastAPI up"}

# Entrypoint for running via `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
