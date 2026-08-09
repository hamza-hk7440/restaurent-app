from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

class IEventStore(ABC):
    """
    Interface for storing and retrieving domain events
    
    Enables event sourcing pattern
    """
    
    @abstractmethod
    async def append(self, event: DomainEvent) -> None:
        """
        Store event
        
        Args:
            event: Domain event to store
        """
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        """
        Get all events for an aggregate
        
        Args:
            aggregate_id: ID of entity
            
        Returns:
            List of events
        """
        pass
    
    @abstractmethod
    async def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        """
        Get all events of specific type
        
        Args:
            event_type: Type of event
            
        Returns:
            List of events
        """
        pass
    
    @abstractmethod
    async def get_all_events(self) -> List[DomainEvent]:
        """
        Get all stored events
        
        Returns:
            List of all events
        """
        pass