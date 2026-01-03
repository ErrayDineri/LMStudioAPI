# LM Studio FastAPI Service

A clean, hybrid FastAPI service for local LLMs and VLMs via LM Studio, combining the best of both worlds:
- **LM Studio SDK** for model management (loading/unloading)
- **OpenAI SDK** for chat operations (cleaner, standard API)

## Features

- 🔄 **Model Management**: Load/unload models programmatically
- 💬 **Flexible Chat**: Generic endpoint or specialized (regular/vision)
- 🎯 **Default Models**: Pre-configured models for common tasks
- 🖼️ **Vision Support**: Full VLM support with base64 images
- 🌊 **Streaming**: NDJSON streaming for real-time responses
- 🔌 **Hybrid Architecture**: LM Studio SDK + OpenAI SDK

## Requirements

- **LM Studio** app running locally
- **Python 3.10+**
- Models downloaded in LM Studio (e.g., `qwen/qwen3-4b-2507`, `qwen3-vl-4b-instruct`)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Default configuration:
```env
# OpenAI-compatible endpoint (LM Studio)
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio

# Server settings
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=*

# Default models for specialized endpoints
DEFAULT_REGULAR_MODEL=qwen/qwen3-4b-2507
DEFAULT_VISION_MODEL=qwen3-vl-4b-instruct
```

### 3. Run the Service

```bash
python main.py
```

Service starts at `http://127.0.0.1:8000`

## API Endpoints

### Health & Info

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/help` | API documentation |

### Model Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/models` | List loaded models |
| POST | `/models/load` | Load a model |
| POST | `/models/unload` | Unload model(s) |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Generic chat (custom model) |
| POST | `/chat/stream` | Generic streaming chat |
| POST | `/chat/regular` | Text-only chat (default model) |
| POST | `/chat/regular/stream` | Text-only streaming |
| POST | `/chat/vision` | Vision chat (default VLM) |
| POST | `/chat/vision/stream` | Vision streaming |

## Usage Examples

### Model Management

#### Load a Model

```powershell
# Load regular model (exclusive - unloads others)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models/load" `
  -Method Post -ContentType 'application/json' `
  -Body '{"model_key":"qwen/qwen3-4b-2507","exclusive":true}'
```

#### List Loaded Models

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models" -Method Get
```

#### Unload Models

```powershell
# Unload specific model
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models/unload" `
  -Method Post -ContentType 'application/json' `
  -Body '{"model_key":"qwen/qwen3-4b-2507"}'

# Unload all models
Invoke-RestMethod -Uri "http://127.0.0.1:8000/models/unload" `
  -Method Post -ContentType 'application/json' `
  -Body '{"unload_all":true}'
```

### Regular Chat (Text-Only)

#### Non-Streaming

```bash
curl -X POST http://127.0.0.1:8000/chat/regular \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is 2+2?"}
    ],
    "config": {
      "temperature": 0.7,
      "maxTokens": 100
    }
  }'
```

PowerShell:
```powershell
$body = @{
  messages = @(
    @{role="system"; content="You are helpful."}
    @{role="user"; content="What is 2+2?"}
  )
  config = @{temperature=0.7; maxTokens=100}
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat/regular" `
  -Method Post -ContentType 'application/json' -Body $body
```

#### Streaming

```bash
curl -N -X POST http://127.0.0.1:8000/chat/regular/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum physics in one sentence"}
    ]
  }'
```

### Vision Chat (With Images)

#### Non-Streaming

```bash
curl -X POST http://127.0.0.1:8000/chat/vision \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is in this image?",
        "images": [{
          "data_base64": "<BASE64_ENCODED_IMAGE>",
          "mime_type": "image/jpeg"
        }]
      }
    ],
    "config": {
      "temperature": 0.6,
      "maxTokens": 200
    }
  }'
```

PowerShell:
```powershell
$imageBytes = [System.IO.File]::ReadAllBytes("path\to\image.jpg")
$base64 = [System.Convert]::ToBase64String($imageBytes)

$body = @{
  messages = @(
    @{
      role = "user"
      content = "Describe this image"
      images = @(
        @{
          data_base64 = $base64
          mime_type = "image/jpeg"
        }
      )
    }
  )
  config = @{temperature=0.7; maxTokens=256}
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat/vision" `
  -Method Post -ContentType 'application/json' -Body $body
```

#### Streaming

```bash
curl -N -X POST http://127.0.0.1:8000/chat/vision/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Describe this image in detail",
        "images": [{
          "data_base64": "<BASE64_ENCODED_IMAGE>",
          "mime_type": "image/jpeg"
        }]
      }
    ]
  }'
```

### Custom Model Chat

Use the generic `/chat` endpoint to specify any model:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model_key": "my-custom-model",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Request/Response Formats

### Chat Request

```json
{
  "model_key": "optional-model-name",
  "messages": [
    {
      "role": "system|user|assistant",
      "content": "message text",
      "images": [
        {
          "data_base64": "base64_string",
          "mime_type": "image/jpeg"
        }
      ]
    }
  ],
  "config": {
    "temperature": 0.7,
    "maxTokens": 100,
    "topP": 0.9,
    "presencePenalty": 0.0,
    "frequencyPenalty": 0.0
  }
}
```

### Chat Response

```json
{
  "model": "model-name",
  "content": "response text",
  "stop_reason": "stop",
  "predicted_tokens": 42
}
```

### Streaming Response (NDJSON)

Each line is a JSON object:

```json
{"type": "fragment", "content": "Hello"}
{"type": "fragment", "content": " world"}
{"type": "done", "model": "model-name", "predicted_tokens": 2, "stop_reason": "stop"}
```

## Configuration

### Chat Config Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | float | Randomness (0.0-2.0). Higher = more random |
| `maxTokens` | int | Maximum tokens to generate |
| `topP` | float | Nucleus sampling (0.0-1.0) |
| `presencePenalty` | float | Penalize new topics (-2.0 to 2.0) |
| `frequencyPenalty` | float | Penalize repetition (-2.0 to 2.0) |

### Image Format

- **Supported formats**: JPEG, PNG, WebP
- **Encoding**: Base64 string
- **Format**: `data:{mime_type};base64,{base64_string}`
- **Mime types**: `image/jpeg`, `image/png`, `image/webp`

## Architecture

### Hybrid Design

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│                                         │
│  Model Management    │    Chat Ops     │
│  (LM Studio SDK)     │  (OpenAI SDK)   │
│                      │                  │
│  • load_model()      │  • chat()       │
│  • unload_model()    │  • stream()     │
│  • list_models()     │  • vision()     │
│                      │                  │
└──────────┬───────────┴─────────┬────────┘
           │                     │
           ▼                     ▼
    ┌─────────────────────────────────┐
    │       LM Studio Server          │
    │  • Model Loading/Unloading      │
    │  • OpenAI-Compatible Endpoint   │
    │    (http://localhost:1234/v1)   │
    └─────────────────────────────────┘
```

### Why Hybrid?

1. **Model Management**: LM Studio SDK provides native control over model lifecycle
2. **Chat Operations**: OpenAI SDK offers cleaner, standard API format
3. **Best of Both**: Combines powerful model control with simple chat interface

## Error Handling

### Common Issues

#### LM Studio Not Running
```json
{
  "detail": "Could not connect to LM Studio: Connection refused"
}
```
**Solution**: Start LM Studio application

#### Model Not Found
```json
{
  "loaded": false,
  "error": "Failed to load model: Model not found"
}
```
**Solution**: Download the model in LM Studio first

#### No Model Loaded
```json
{
  "detail": "Chat service unavailable: No model loaded"
}
```
**Solution**: Load a model via `/models/load` or LM Studio UI

## Development

### Project Structure

```
back/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Configuration (not in git)
├── .env.example         # Configuration template
└── app/
    ├── config.py        # Settings management
    ├── schemas.py       # Pydantic models
    ├── services.py      # Business logic (OpenAI SDK)
    ├── model_manager.py # Model management (LM Studio SDK)
    └── routes/
        ├── chat.py      # Chat endpoints
        ├── models.py    # Model management endpoints
        ├── health.py    # Health check
        └── help.py      # API documentation
```

### Running Tests

```bash
pytest
```

## License

[Add your license here]

## Support

For issues and questions:
- LM Studio: https://lmstudio.ai/docs
- OpenAI SDK: https://platform.openai.com/docs
