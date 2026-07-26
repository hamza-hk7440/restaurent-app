from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db_session: Session, model_class):
        self.db=db_session
        self.model_class=model_class
    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first()
    def get_all(self) -> List[T]:
        return self.db.query(self.model_class).all()
    def update(self, entity: T) -> T:
        self.db.merge(entity)
        self.db.commit()
        return entity
    def delete(self, id: UUID) -> None:
        record=self.get_by_id(id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False
    def exists(self, entity_id: UUID) -> bool:
        return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first() is not None