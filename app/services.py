from typing import Optional, AsyncIterable
from functools import lru_cache
import time
import logging
import httpx
from openai import AsyncOpenAI

from .config import get_settings

# Setup logging for performance tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache
def get_client() -> AsyncOpenAI:
    """Get configured async OpenAI client for LM Studio (cached singleton)."""
    start = time.perf_counter()
    settings = get_settings()
    # Use httpx.Timeout for granular control:
    # - connect: 10 seconds to establish connection
    # - read: configurable (default 300s) for streaming responses from LLM
    # - write: 30 seconds for sending requests
    # - pool: 10 seconds for acquiring connection from pool
    timeout = httpx.Timeout(
        connect=10.0,
        read=settings.llm_timeout,
        write=30.0,
        pool=10.0,
    )
    client = AsyncOpenAI(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        timeout=timeout,
    )
    logger.info(f"[PERF] Client created in {(time.perf_counter() - start)*1000:.2f}ms")
    return client


def build_messages(messages: list[dict]) -> list[dict]:
    """
    Build OpenAI-compatible messages from request payload.
    Handles image preparation for VLM (Vision-Language Model) inputs.
    """
    formatted_messages = []
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        images = msg.get("images", []) or []
        
        if not images:
            # Text-only message
            formatted_messages.append({
                "role": role,
                "content": content
            })
        else:
            # Message with images (for vision models)
            content_parts = []
            
            # Add text content
            if content:
                content_parts.append({
                    "type": "text",
                    "text": content
                })
            
            # Add images
            for img in images:
                b64 = img.get("data_base64")
                mime_type = img.get("mime_type", "image/jpeg")
                if b64:
                    # OpenAI format: data URL with base64 image
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64}"
                        }
                    })
            
            formatted_messages.append({
                "role": role,
                "content": content_parts
            })
    
    return formatted_messages


async def respond(messages: list[dict], model_key: Optional[str], config: Optional[dict]) -> dict:
    """Non-streaming chat completion (async)."""
    total_start = time.perf_counter()
    
    t0 = time.perf_counter()
    settings = get_settings()
    logger.info(f"[PERF] get_settings: {(time.perf_counter() - t0)*1000:.2f}ms")
    
    t0 = time.perf_counter()
    client = get_client()
    logger.info(f"[PERF] get_client: {(time.perf_counter() - t0)*1000:.2f}ms")
    
    # Use provided model or default
    model = model_key or settings.default_regular_model
    
    # Build messages
    t0 = time.perf_counter()
    formatted_messages = build_messages(messages)
    logger.info(f"[PERF] build_messages: {(time.perf_counter() - t0)*1000:.2f}ms")
    
    # Prepare config
    cfg = config or {}
    params = {
        "model": model,
        "messages": formatted_messages,
    }
    
    # Map our config to OpenAI parameters
    if "temperature" in cfg:
        params["temperature"] = cfg["temperature"]
    if "maxTokens" in cfg:
        params["max_tokens"] = cfg["maxTokens"]
    if "topP" in cfg:
        params["top_p"] = cfg["topP"]
    if "presencePenalty" in cfg:
        params["presence_penalty"] = cfg["presencePenalty"]
    if "frequencyPenalty" in cfg:
        params["frequency_penalty"] = cfg["frequencyPenalty"]
    
    # Make async API call
    t0 = time.perf_counter()
    logger.info(f"[PERF] Calling LLM API with model: {model}")
    response = await client.chat.completions.create(**params)
    logger.info(f"[PERF] LLM API response: {(time.perf_counter() - t0)*1000:.2f}ms")
    
    logger.info(f"[PERF] Total respond(): {(time.perf_counter() - total_start)*1000:.2f}ms")
    
    return {
        "model": response.model,
        "content": response.choices[0].message.content,
        "stop_reason": response.choices[0].finish_reason,
        "predicted_tokens": response.usage.completion_tokens if response.usage else None,
    }


async def stream_respond(messages: list[dict], model_key: Optional[str], config: Optional[dict]) -> AsyncIterable[dict]:
    """Streaming chat completion (async generator)."""
    total_start = time.perf_counter()
    
    settings = get_settings()
    client = get_client()
    
    # Use provided model or default
    model = model_key or settings.default_regular_model
    
    # Build messages
    formatted_messages = build_messages(messages)
    
    # Prepare config
    cfg = config or {}
    params = {
        "model": model,
        "messages": formatted_messages,
        "stream": True,
    }
    
    # Map our config to OpenAI parameters
    if "temperature" in cfg:
        params["temperature"] = cfg["temperature"]
    if "maxTokens" in cfg:
        params["max_tokens"] = cfg["maxTokens"]
    if "topP" in cfg:
        params["top_p"] = cfg["topP"]
    if "presencePenalty" in cfg:
        params["presence_penalty"] = cfg["presencePenalty"]
    if "frequencyPenalty" in cfg:
        params["frequency_penalty"] = cfg["frequencyPenalty"]
    
    # Make async streaming API call
    logger.info(f"[PERF] stream_respond setup: {(time.perf_counter() - total_start)*1000:.2f}ms")
    t0 = time.perf_counter()
    stream = await client.chat.completions.create(**params)
    logger.info(f"[PERF] LLM stream created: {(time.perf_counter() - t0)*1000:.2f}ms")
    
    model_name = None
    total_tokens = 0
    finish_reason = None
    first_token_time = None
    
    async for chunk in stream:
        if first_token_time is None:
            first_token_time = time.perf_counter()
            logger.info(f"[PERF] Time to first token: {(first_token_time - total_start)*1000:.2f}ms")
        
        if chunk.choices:
            choice = chunk.choices[0]
            
            # Get model name from first chunk
            if model_name is None and chunk.model:
                model_name = chunk.model
            
            # Get content delta
            if choice.delta and choice.delta.content:
                yield {
                    "type": "fragment",
                    "content": choice.delta.content
                }
                total_tokens += 1
            
            # Get finish reason
            if choice.finish_reason:
                finish_reason = choice.finish_reason
    
    # Yield final message
    yield {
        "type": "done",
        "model": model_name or model,
        "predicted_tokens": total_tokens if total_tokens > 0 else None,
        "stop_reason": finish_reason
    }


async def respond_regular(messages: list[dict], config: Optional[dict]) -> dict:
    """Handle regular chat requests with default model for text-only tasks."""
    settings = get_settings()
    model_key = settings.default_regular_model
    return await respond(messages, model_key, config)


async def stream_respond_regular(messages: list[dict], config: Optional[dict]) -> AsyncIterable[dict]:
    """Handle streaming regular chat requests with default model for text-only tasks."""
    settings = get_settings()
    model_key = settings.default_regular_model
    async for item in stream_respond(messages, model_key, config):
        yield item


async def respond_vision(messages: list[dict], config: Optional[dict]) -> dict:
    """Handle vision chat requests with default model for visual tasks."""
    settings = get_settings()
    model_key = settings.default_vision_model
    return await respond(messages, model_key, config)


async def stream_respond_vision(messages: list[dict], config: Optional[dict]) -> AsyncIterable[dict]:
    """Handle streaming vision chat requests with default model for visual tasks."""
    settings = get_settings()
    model_key = settings.default_vision_model
    async for item in stream_respond(messages, model_key, config):
        yield item
