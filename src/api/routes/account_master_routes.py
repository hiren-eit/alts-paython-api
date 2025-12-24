from fastapi import APIRouter
from src.api.controllers import account_master_controller

router = APIRouter()
router.include_router(account_master_controller.router)
