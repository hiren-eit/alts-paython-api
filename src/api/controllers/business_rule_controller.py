from typing import Optional
from src.domain.dtos.business_rule_request import BusinessRuleRequest
from src.domain.dtos.business_rule_api_input import GetBusinessRuleApiInput
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from importlib import import_module
from src.api.controllers.base_controller import BaseController
from src.infrastructure.database.connection_manager import get_db
from src.domain.services.business_rule_service import BusinessRuleService
from src.infrastructure.logging.logger_manager import get_logger
from src.core.settings import get_connection_config

# Initialize Logger
logger = get_logger(__name__)

# Initialize Router
router = APIRouter(prefix="/business-rules", tags=["BusinessRule"])


def get_business_rule_service(db: Session = Depends(get_db)) -> BusinessRuleService:
    """
    Dependency provider for BusinessRuleService.
    Dynamically loads the repository based on the active connection configuration.
    """
    try:
        _, active_repository_path = get_connection_config()
        # Dynamic Repository Import
        module_path = f"{active_repository_path}.business_rule_repository"
        repository_module = import_module(module_path)
        business_rule_repository_cls = getattr(repository_module, "BusinessRuleRepository")
        
        repository = business_rule_repository_cls()
        return BusinessRuleService(repository)
    except (ImportError, AttributeError) as e:
        logger.critical(f"Failed to load BusinessRuleRepository: {e}", exc_info=True)
        raise RuntimeError("Configuration error: Repository could not be loaded.")


class BusinessRuleController(BaseController):
    """
    Controller for managing Business Rules.
    Provides endpoints for creating, updating, listing, and applying business rules.
    """

    @router.post("/", response_model=Dict[str, Any], summary="Create a new Business Rule")
    def create_rule(
        rule_data: BusinessRuleRequest = Body(..., description="The business rule data to create"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Create a new business rule in the system.
        """
        logger.info("Request received to create a new business rule.")
        return BaseController.safe_execute(lambda: 
            BaseController.success_response(service.save_rule(db, rule_data.model_dump()), "Rule successfully created")
        )

    @router.put("/", response_model=Dict[str, Any], summary="Update an existing Business Rule")
    def update_rule(
        rule_data: BusinessRuleRequest = Body(..., description="The business rule data to update"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Update an existing business rule.
        """
        logger.info("Request received to update a business rule.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.update_rule(db, rule_data.model_dump()), "Rule successfully updated")
        )

    @router.post("/clone", response_model=Dict[str, Any], summary="Clone a Business Rule")
    def clone_rule(
        rule_data: BusinessRuleRequest = Body(..., description="The business rule data to clone"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Clone an existing business rule to create a new one.
        """
        logger.info("Request received to clone a business rule.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.clone_rule(db, rule_data.model_dump()), "Rule successfully cloned")
        )

    # @router.get("/", response_model=Dict[str, Any], summary="List Business Rules or Get Details")
    # def list_rules_or_get_details(
    #     input_data: Dict[str, Any] = Depends(), 
    #     service: BusinessRuleService = Depends(get_business_rule_service),
    #     db: Session = Depends(get_db)
    # ):
    #     """
    #     Get a list of business rules or specific rule details based on input.
    #     """
    #     # Note: The original code had two GET routes impacting root or list logic.
    #     # Merging logic if necessary or keeping distinct paths if they conflict.
    #     # Original: @router.get("/") was get_business_rule_api
    #     # Original: @router.get("/list") was get_rule_list
    #     # Since input_data is a dependency, it might be ambiguous unless strictly typed.
    #     # Ideally, we keep /list explicit if the root / expects query params for a specific item.
    #     # For this refactor, I will keep /list as a clear collection resource and / as the details/search.
    #     logger.info("Request received to get business rule details.")
    #     return BaseController.safe_execute(lambda:
    #         BaseController.success_response(service.get_business_rule_api(db, input_data))
    #     )

    @router.post("/get-business-rule-api", response_model=Dict[str, Any], summary="Get Business Rule Data")
    def get_business_rule_api(
        input_data: GetBusinessRuleApiInput = Body(...),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Retrieve business rule data with complex filtering, sorting, and pagination.
        """
        logger.info("Request received to get Business Rule data.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.get_business_rule_api(db, input_data))
        )

    # @router.get("/list", response_model=Dict[str, Any], summary="List all Business Rules")

    @router.patch("/toggle", response_model=Dict[str, Any], summary="Toggle Business Rule Status")
    def toggle_rule_status(
        rule_data: BusinessRuleRequest = Body(..., description="Data identifying the rule to toggle"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Toggle the active status of a business rule.
        """
        logger.info("Request received to toggle business rule status.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.toggle_business_rule(db, rule_data.model_dump()))
        )

    @router.patch("/stage", response_model=Dict[str, Any], summary="Update Business Rule Stage")
    def update_rule_stage(
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Update the stage of business rules.
        """
        logger.info("Request received to update business rule stage.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.update_stage(db))
        )

    @router.post("/apply", response_model=Dict[str, Any], summary="Apply Business Rules")
    def apply_rules(
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Trigger the application of business rules.
        """
        # Changed to POST as 'apply' implies an action/state change, not just data retrieval.
        # Original was GET, but side-effects suggest POST.
        # User asked for clean code.
        logger.info("Request received to apply business rules.")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.apply_business_rule_api(db))
        )

    @router.get("/filter", response_model=Dict[str, Any], summary="Filter Business Rules")
    def filter_rules(
        filter_field: str = Query(..., alias="FilterField"),
        source_type: str = Query(..., alias="SourceType"),
        rule_type: str = Query(..., alias="RuleType"),
        content_type: Optional[str] = Query(None, alias="ContentType"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Filter business rules based on specific criteria.
        """
        logger.info(f"Request received to filter business rules by field: {filter_field}")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.get_business_filter_by_field(db, filter_field, source_type, rule_type, content_type))
        )

    @router.get("/log", response_model=Dict[str, Any], summary="Get Business Rule Log")
    def get_rule_logs(
        rule_id: str = Query(..., alias="Id", description="The ID of the rule"),
        service: BusinessRuleService = Depends(get_business_rule_service),
        db: Session = Depends(get_db)
    ):
        """
        Retrieve logs associated with a specific business rule.
        """
        logger.info(f"Request received to get logs for rule ID: {rule_id}")
        return BaseController.safe_execute(lambda:
            BaseController.success_response(service.get_business_rule_log(db, rule_id))
        )

    # @router.post("/usage-log", response_model=Dict[str, Any], summary="Get Usage Log")
    # def get_usage_log(
    #     input_model: Dict[str, Any] = Body(...),
    #     service: BusinessRuleService = Depends(get_business_rule_service),
    #     db: Session = Depends(get_db)
    # ):
    #     """
    #     Retrieve usage logs based on input criteria.
    #     """
    #     logger.info("Request received to get usage logs.")
    #     return BaseController.safe_execute(lambda:
    #         BaseController.success_response(service.get_usage_log_by_rule_api(db, input_model))
    #     )
