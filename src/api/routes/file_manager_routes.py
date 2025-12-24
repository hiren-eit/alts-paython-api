from fastapi import APIRouter
from src.api.controllers import file_manager_controller

router = APIRouter()
router.include_router(file_manager_controller.router)
