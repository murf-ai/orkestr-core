import asyncio
from .event_library.event import Event
from typing import Callable, Dict, Set, Coroutine, Type
from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

class AsyncEventBus:
    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.loop = asyncio.get_event_loop()

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type with a callback"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = set()
        self.subscribers[event_type].add(callback)

    def subscribe_to_event(self, event_class: Type[Event], callback: Callable):
        """Subscribe to events of a specific model class"""
        event_type = event_class.event_type
        self.subscribe(event_type, callback)
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            
    def emit(self, event: Event):
        """Non-blocking event emission that schedules all callbacks asynchronously"""
        event_type = event.get_event_type()
        logger.info(f"Emitting event: {event_type} with data: {event.model_dump()}")
        listeners = self.subscribers.get(event_type, set())
        for listener in listeners:
            # Create a task for each listener, allowing them to run concurrently
            asyncio.create_task(self._run_callback(listener, event))
            
    async def _run_callback(self, callback: Callable | Coroutine, event: Event):
        """Helper method to handle both regular functions and coroutines"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                # Run synchronous callbacks in the executor to avoid blocking
                await self.loop.run_in_executor(None, callback, event)
        except Exception as e:
            logger.error(f"Error occurred while executing callback for event: {e}", exc_info=True)
