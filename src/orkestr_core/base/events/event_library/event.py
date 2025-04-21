from enum import Enum
from typing import Union, ClassVar
from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    """Base class for all events"""
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Class variable that subclasses will override
    event_type: ClassVar[str] = "base.event"
    
    def get_event_type(self) -> str:
        """Get the event type from the class variable"""
        return self.__class__.event_type