from fastapi import APIRouter
from src.api.controllers import file_service_controller

router = APIRouter()
router.include_router(file_service_controller.router)