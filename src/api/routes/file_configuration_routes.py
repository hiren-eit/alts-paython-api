from fastapi import APIRouter
from src.api.controllers import file_configuration_controller

router = APIRouter()
router.include_router(file_configuration_controller.router)
