"""
Model management using LM Studio SDK.
Handles loading/unloading models while chat operations use OpenAI SDK.
"""
import lmstudio as lms
from typing import Optional

class ModelNotAvailable(Exception):
    pass


class ModelManager:
    """Simplified model manager for loading/unloading models via LM Studio SDK."""
    
    @staticmethod
    def list_models() -> list[dict]:
        """List all loaded models."""
        try:
            models = lms.list_loaded_models("llm")
        except Exception as e:
            raise ModelNotAvailable(f"Could not connect to LM Studio: {e}")
        
        result = []
        for model in models:
            try:
                info = model.get_info()
                model_key = getattr(info, "modelKey", None)
                display_name = getattr(info, "displayName", None)
                
                if not model_key:
                    continue
                
                result.append({
                    "key": model_key,
                    "display_name": display_name or model_key,
                })
            except Exception:
                continue
        
        return result
    
    @staticmethod
    def load_model(model_key: str, exclusive: bool = False) -> dict:
        """Load a model. If exclusive=True, unload others first."""
        try:
            if exclusive:
                ModelManager.unload_all()
            
            # Load the model using LM Studio SDK
            model = lms.llm(model_key)
            
            # Get model info
            try:
                info = model.get_info()
                display_name = getattr(info, "displayName", model_key)
            except Exception:
                display_name = model_key
            
            return {
                "key": model_key,
                "display_name": display_name,
            }
        except Exception as e:
            raise ModelNotAvailable(f"Failed to load model {model_key}: {e}")
    
    @staticmethod
    def unload_model(model_key: str) -> bool:
        """Unload a specific model."""
        try:
            model = lms.llm(model_key)
            model.unload()
            return True
        except Exception as e:
            raise ModelNotAvailable(f"Failed to unload model {model_key}: {e}")
    
    @staticmethod
    def unload_all() -> list[str]:
        """Unload all loaded models."""
        unloaded = []
        try:
            models = lms.list_loaded_models("llm")
            for model in models:
                try:
                    info = model.get_info()
                    key = getattr(info, "modelKey", None)
                    model.unload()
                    if key:
                        unloaded.append(key)
                except Exception:
                    continue
        except Exception:
            pass
        
        return unloaded
