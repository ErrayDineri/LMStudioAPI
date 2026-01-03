import json
import time
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas import ChatRequest, StreamChatRequest, ChatResponse, RegularChatRequest, VisionChatRequest, StreamRegularChatRequest, StreamVisionChatRequest
from ..services import respond, stream_respond, respond_regular, stream_respond_regular, respond_vision, stream_respond_vision

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Generic chat endpoint with custom model selection."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Chat request received ===")
    
    try:
        t0 = time.perf_counter()
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
        logger.info(f"[PERF] Request parsing: {(time.perf_counter() - t0)*1000:.2f}ms")
        
        t0 = time.perf_counter()
        data = await respond(messages, req.model_key, config)
        logger.info(f"[PERF] respond() call: {(time.perf_counter() - t0)*1000:.2f}ms")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")
    
    logger.info(f"[PERF] === Total request time: {(time.perf_counter() - request_start)*1000:.2f}ms ===")
    return ChatResponse(**data)

@router.post("/stream")
async def chat_stream(req: StreamChatRequest):
    """Generic streaming chat endpoint with custom model selection."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Stream chat request received ===")
    
    try:
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")

    async def event_gen():
        async for item in stream_respond(messages, req.model_key, config):
            yield json.dumps(item) + "\n"
        logger.info(f"[PERF] === Stream completed: {(time.perf_counter() - request_start)*1000:.2f}ms ===")

    return StreamingResponse(event_gen(), media_type="application/x-ndjson")


@router.post("/regular", response_model=ChatResponse)
async def chat_regular(req: RegularChatRequest):
    """Chat endpoint for regular text-only tasks using the default regular model."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Regular chat request received ===")
    
    try:
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
        data = await respond_regular(messages, config)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")
    
    logger.info(f"[PERF] === Total request time: {(time.perf_counter() - request_start)*1000:.2f}ms ===")
    return ChatResponse(**data)


@router.post("/regular/stream")
async def chat_regular_stream(req: StreamRegularChatRequest):
    """Streaming chat endpoint for regular text-only tasks using the default regular model."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Regular stream request received ===")
    
    try:
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")

    async def event_gen():
        async for item in stream_respond_regular(messages, config):
            yield json.dumps(item) + "\n"
        logger.info(f"[PERF] === Stream completed: {(time.perf_counter() - request_start)*1000:.2f}ms ===")

    return StreamingResponse(event_gen(), media_type="application/x-ndjson")


@router.post("/vision", response_model=ChatResponse)
async def chat_vision(req: VisionChatRequest):
    """Chat endpoint for visual tasks using the default vision model."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Vision chat request received ===")
    
    try:
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
        data = await respond_vision(messages, config)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")
    
    logger.info(f"[PERF] === Total request time: {(time.perf_counter() - request_start)*1000:.2f}ms ===")
    return ChatResponse(**data)


@router.post("/vision/stream")
async def chat_vision_stream(req: StreamVisionChatRequest):
    """Streaming chat endpoint for visual tasks using the default vision model."""
    request_start = time.perf_counter()
    logger.info("[PERF] === Vision stream request received ===")
    
    try:
        messages = [m.model_dump() for m in req.messages]
        config = req.config.model_dump(exclude_none=True) if req.config else None
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Chat service unavailable: {e}")

    async def event_gen():
        async for item in stream_respond_vision(messages, config):
            yield json.dumps(item) + "\n"
        logger.info(f"[PERF] === Stream completed: {(time.perf_counter() - request_start)*1000:.2f}ms ===")

    return StreamingResponse(event_gen(), media_type="application/x-ndjson")
