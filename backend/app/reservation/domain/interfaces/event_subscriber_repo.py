from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

class IEventSubscriber(ABC):
    """
    Interface for subscribing to domain events
    
    Implementations handle specific event types
    """
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle event
        
        Args:
            event: Domain event to handle
        """
        pass
    
    @abstractmethod
    def supports_event(self, event: DomainEvent) -> bool:
        """
        Check if subscriber handles this event type
        
        Args:
            event: Domain event to check
            
        Returns:
            bool: True if subscriber handles this event
        """
        pass