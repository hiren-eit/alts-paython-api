from fastapi import APIRouter
from src.api.controllers import file_router_controller

router = APIRouter()
router.include_router(file_router_controller.router)