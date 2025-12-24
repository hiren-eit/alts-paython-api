from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from src.infrastructure.database.base_repository import BaseRepository

class IBusinessRuleRepository(BaseRepository, ABC):
    @abstractmethod
    def save_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def clone_rule(self, db: Session, rule: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_business_rules_api(self, db: Session) -> List[Any]:
        pass

    @abstractmethod
    def toggle_rule(self, db: Session, rule: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def update_stage(self, db: Session) -> Any:
        pass

    @abstractmethod
    def apply_business_rule_api_async(self, db: Session) -> int:
        pass

    @abstractmethod
    def get_business_rule_data(self, db: Session, input_data: Any) -> Any:
        pass

    @abstractmethod
    def get_business_filter_by_field(self, db: Session, filter_field: str, source_type: str, rule_type: str, content_type: str) -> Any:
        pass

    @abstractmethod
    def get_business_rule_log_data(self, db: Session, rule_id: str) -> Any:
        pass

    @abstractmethod
    def get_usage_log_by_rule_async(self, db: Session, input_model: Any) -> Any:
        pass
