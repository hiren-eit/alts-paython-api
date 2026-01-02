from fastapi import APIRouter
from src.api.controllers import master_configuration_type_controller

router = APIRouter()
router.include_router(master_configuration_type_controller.router)
