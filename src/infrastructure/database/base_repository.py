from typing import Any, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.infrastructure.logging.logger_manager import get_logger

# Define generic types for Model, CreateSchema, and UpdateSchema
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = get_logger(__name__)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base Repository class with default CRUD operations, logging, and error handling.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        try:
            logger.info(f"Fetching {self.model.__name__} by id: {id}")
            result = db.query(self.model).filter(self.model.id == id).first()
            if not result:
                logger.warning(f"{self.model.__name__} with id {id} not found.")
            return result
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by id {id}: {e}", exc_info=True)
            raise

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            logger.info(f"Fetching all {self.model.__name__} records with skip={skip}, limit={limit}")
            return db.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching all {self.model.__name__} records: {e}", exc_info=True)
            raise

    def create(self, db: Session, obj_in: Union[CreateSchemaType, dict]) -> ModelType:
        try:
            logger.info(f"Creating new {self.model.__name__}")
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Successfully created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}", exc_info=True)
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict, Any]
    ) -> ModelType:
        try:
            logger.info(f"Updating {self.model.__name__} with id: {db_obj.id}") # type: ignore
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Successfully updated {self.model.__name__}")
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}", exc_info=True)
            db.rollback()
            raise

    def delete(self, db: Session, *, id: int) -> ModelType:
        try:
            logger.info(f"Deleting {self.model.__name__} with id: {id}")
            obj = db.query(self.model).get(id)
            if not obj:
                logger.warning(f"Attempted to delete non-existent {self.model.__name__} with id {id}")
                return None # or raise Logic? generic usually returns None or raises
            
            db.delete(obj)
            db.commit()
            logger.info(f"Successfully deleted {self.model.__name__}")
            return obj
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}", exc_info=True)
            db.rollback()
            raise
