from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod

@dataclass
class DomainEvent(ABC):   
    event_id: UUID
    event_type: str
    aggregate_id: UUID  
    occurred_at: datetime
    version: int = 1
    
    @abstractmethod
    def get_event_name(self) -> str:
        pass