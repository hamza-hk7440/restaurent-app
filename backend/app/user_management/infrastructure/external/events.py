from user_management.domain.interfaces.events_repo import IEventRepository

class EventRepository(IEventRepository):
    def __init__(self):
        self._handlers = {}
    async def dispatch(self, event):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)
                