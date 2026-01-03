from pydantic import BaseModel, Field
from typing import List, Optional

class ChatImage(BaseModel):
    data_base64: str = Field(..., description="Base64 encoded image (JPEG/PNG/WebP)")
    mime_type: str | None = Field(default="image/jpeg", description="MIME type of the image")

class ChatMessage(BaseModel):
    role: str = Field(..., description="system|user|assistant")
    content: str = Field("", description="Text content of the message")
    images: List[ChatImage] = Field(default_factory=list, description="Optional images for VLM input")

class ChatConfig(BaseModel):
    temperature: float | None = None
    maxTokens: int | None = None
    topP: float | None = None
    presencePenalty: float | None = None
    frequencyPenalty: float | None = None

class ChatRequest(BaseModel):
    model_key: Optional[str] = Field(None, description="Optional model key to use")
    messages: List[ChatMessage]
    config: Optional[ChatConfig] = None

class StreamChatRequest(ChatRequest):
    pass

class RegularChatRequest(BaseModel):
    messages: List[ChatMessage]
    config: Optional[ChatConfig] = None

class VisionChatRequest(BaseModel):
    messages: List[ChatMessage]
    config: Optional[ChatConfig] = None

class StreamRegularChatRequest(RegularChatRequest):
    pass

class StreamVisionChatRequest(VisionChatRequest):
    pass

class ChatResponse(BaseModel):
    model: str
    content: str
    stop_reason: Optional[str] = None
    predicted_tokens: Optional[int] = None

class ModelInfo(BaseModel):
    key: str
    display_name: str | None = None

class LoadModelRequest(BaseModel):
    model_key: str
    exclusive: bool = Field(default=False, description="If True, unload other models before loading")

class LoadModelResponse(BaseModel):
    loaded: bool
    model: Optional[ModelInfo] = None
    error: Optional[str] = None

class UnloadModelRequest(BaseModel):
    model_key: Optional[str] = Field(default=None, description="Model to unload, or omit with unload_all=True")
    unload_all: bool = Field(default=False, description="If True, unload all models")

class UnloadModelResponse(BaseModel):
    success: bool
    unloaded_keys: list[str] = Field(default_factory=list)
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
