from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

class IEventPublisher(ABC):
    """
    Interface for publishing domain events
    
    Implementations handle event distribution to subscribers
    """
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish event to all subscribers
        
        Args:
            event: Domain event to publish
        """
        pass
    
    @abstractmethod
    async def publish_multiple(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple events
        
        Args:
            events: List of domain events to publish
        """
        pass
