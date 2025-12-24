from fastapi import APIRouter
from src.api.controllers import file_activity_controller

router = APIRouter()
router.include_router(file_activity_controller.router)
