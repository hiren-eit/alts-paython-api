from fastapi import APIRouter
from src.api.controllers import account_linking_master_controller

router = APIRouter()
router.include_router(account_linking_master_controller.router)