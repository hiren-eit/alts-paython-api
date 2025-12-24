from typing import Any, Dict, List
from sqlalchemy.orm import Session
from src.domain.interfaces.business_rule_repository_interface import IBusinessRuleRepository

class BusinessRuleService:
    def __init__(self, repository: IBusinessRuleRepository):
        self.repository = repository

    def save_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        return self.repository.save_rule(db, rule)

    def update_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        return self.repository.update_rule(db, rule)

    def clone_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        return self.repository.clone_rule(db, rule)

    def get_rule_list(self, db: Session) -> List[Any]:
        return self.repository.get_business_rules_api(db)

    def toggle_business_rule(self, db: Session, rule: Dict[str, Any]) -> Any:
        return self.repository.toggle_rule(db, rule)

    def update_stage(self, db: Session) -> Any:
        return self.repository.update_stage(db)

    def apply_business_rule_api(self, db: Session) -> int:
        return self.repository.apply_business_rule_api_async(db)

    def get_business_rule_api(self, db: Session, input_data: Any) -> Any:
        return self.repository.get_business_rule_data(db, input_data)

    def get_business_filter_by_field(self, db: Session, filter_field: str, source_type: str, rule_type: str, content_type: str) -> Any:
        return self.repository.get_business_filter_by_field(db, filter_field, source_type, rule_type, content_type)

    def get_business_rule_log(self, db: Session, rule_id: str) -> Any:
        return self.repository.get_business_rule_log_data(db, rule_id)

    def get_usage_log_by_rule_api(self, db: Session, input_model: Any) -> Any:
        return self.repository.get_usage_log_by_rule_async(db, input_model)
