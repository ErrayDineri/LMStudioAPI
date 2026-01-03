from fastapi import APIRouter, HTTPException
from ..schemas import ModelInfo, LoadModelRequest, LoadModelResponse, UnloadModelRequest, UnloadModelResponse
from ..model_manager import ModelManager, ModelNotAvailable

router = APIRouter(prefix="/models", tags=["models"])

@router.get("", response_model=list[ModelInfo])
async def list_models():
    """List loaded models from LM Studio."""
    try:
        models = ModelManager.list_models()
        return [ModelInfo(**m) for m in models]
    except ModelNotAvailable as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/load", response_model=LoadModelResponse)
async def load_model(req: LoadModelRequest):
    """Load a model in LM Studio."""
    try:
        model_info = ModelManager.load_model(req.model_key, exclusive=req.exclusive)
        return LoadModelResponse(loaded=True, model=ModelInfo(**model_info))
    except ModelNotAvailable as e:
        return LoadModelResponse(loaded=False, error=str(e))

@router.post("/unload", response_model=UnloadModelResponse)
async def unload_model(req: UnloadModelRequest):
    """Unload model(s) from LM Studio."""
    try:
        if req.unload_all:
            unloaded = ModelManager.unload_all()
        elif req.model_key:
            ModelManager.unload_model(req.model_key)
            unloaded = [req.model_key]
        else:
            return UnloadModelResponse(success=False, error="Must specify model_key or unload_all=true")
        
        return UnloadModelResponse(success=True, unloaded_keys=unloaded)
    except ModelNotAvailable as e:
        return UnloadModelResponse(success=False, error=str(e))
