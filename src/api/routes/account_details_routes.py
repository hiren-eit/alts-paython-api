from fastapi import APIRouter
from src.api.controllers import account_details_controller

router = APIRouter()
router.include_router(account_details_controller.router)
