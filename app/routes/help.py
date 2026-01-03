from fastapi import APIRouter

router = APIRouter(prefix="/help", tags=["help"])

HELP_TEXT = {
    "summary": "LM Studio FastAPI endpoints (OpenAI SDK for chat + LM Studio SDK for model management)",
    "routes": [
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check"
        },
        {
            "method": "GET",
            "path": "/models",
            "description": "List loaded models from LM Studio"
        },
        {
            "method": "POST",
            "path": "/models/load",
            "description": "Load a model. Body: { model_key: string, exclusive?: boolean }"
        },
        {
            "method": "POST",
            "path": "/models/unload",
            "description": "Unload model(s). Body: { model_key?: string, unload_all?: boolean }"
        },
        {
            "method": "POST",
            "path": "/chat",
            "description": "Non-streaming chat with custom model. Body: { model_key?, messages: [{role, content, images?}], config? }"
        },
        {
            "method": "POST",
            "path": "/chat/stream",
            "description": "Streaming chat with custom model (NDJSON). Body: { model_key?, messages: [{role, content, images?}], config? }"
        },
        {
            "method": "POST",
            "path": "/chat/regular",
            "description": "Non-streaming text-only chat using default regular model. Body: { messages: [{role, content}], config? }"
        },
        {
            "method": "POST",
            "path": "/chat/regular/stream",
            "description": "Streaming text-only chat using default regular model (NDJSON). Body: { messages: [{role, content}], config? }"
        },
        {
            "method": "POST",
            "path": "/chat/vision",
            "description": "Non-streaming vision chat using default vision model. Body: { messages: [{role, content, images?}], config? }"
        },
        {
            "method": "POST",
            "path": "/chat/vision/stream",
            "description": "Streaming vision chat using default vision model (NDJSON). Body: { messages: [{role, content, images?}], config? }"
        }
    ],
    "notes": [
        "Model management (load/unload) uses LM Studio SDK",
        "Chat operations use OpenAI SDK with LM Studio's OpenAI-compatible API (http://localhost:1234/v1)",
        "Models are loaded/unloaded via LM Studio SDK but chat goes through OpenAI endpoint",
        "messages[].role is one of system|user|assistant",
        "messages[].images[] accepts { data_base64, mime_type? } for vision models (VLM)",
        "Images use data URL format: data:image/jpeg;base64,{base64_string}",
        "Supported image formats: JPEG, PNG, WebP",
        "config supports: temperature, maxTokens, topP, presencePenalty, frequencyPenalty",
        "Default models configured in .env: DEFAULT_REGULAR_MODEL, DEFAULT_VISION_MODEL",
        "Streaming returns application/x-ndjson with one JSON object per line",
        "Use exclusive=true when loading to unload other models first"
    ]
}

@router.get("")
async def get_help():
    return HELP_TEXT
