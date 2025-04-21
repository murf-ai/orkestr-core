from pydantic import BaseModel
from typing import Dict, Optional, Callable, Union, Awaitable, Any
import uuid

class SchedulerAction(BaseModel):
    """
    SchedulerAction is a base class for all actions that can be performed by the scheduler.
    It provides a common interface for all actions and allows for easy extension and modification.
    """
    action_id: str = uuid.uuid4().hex
    action_name: Optional[str] = None
    action_description: Optional[str] = None
    action_parameters: Dict = {}  # Default to an empty dictionary
    action_func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]]

    def execute(self):
        """
        Execute the action.
        """
        if self.action_func:
            return self.action_func(**self.action_parameters)
        else:
            raise NotImplementedError("Action function is not defined.")
