from fastapi import APIRouter
from src.api.controllers import validation_controller

router = APIRouter()
router.include_router(validation_controller.router)
