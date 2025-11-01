from fastapi import APIRouter
from ..utils.model_registry import ModelManager

models_router = APIRouter()


@models_router.get("/list", summary="List supported chat models")
def list_models():
    return {"models": ModelManager.list_models()}
