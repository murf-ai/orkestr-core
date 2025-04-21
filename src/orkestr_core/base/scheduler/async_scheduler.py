import asyncio
from typing import List
from .scheduler_action import SchedulerAction  # Ensure correct import
from orkestr_core.util.logger import setup_logger
import traceback

logger = setup_logger(__name__)

class AsyncScheduler:
    def __init__(self, actions: List[SchedulerAction], interval: float):
        """
        Initialize the AsyncScheduler.

        :param actions: A list of SchedulerAction objects to execute.
        :param interval: Time interval (in seconds) between each execution.
        """
        self.actions = {action.action_id: action for action in actions}  # Store actions by ID
        self.interval = interval
        self._stop_event = asyncio.Event()
        self._task = None  # Will store the main scheduler task

    async def start(self):
        """Start the scheduler as an asyncio task."""
        if self._task and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Stop the scheduler."""
        if self._task:
            self._stop_event.set()
            await self._task
            self._task = None

    def add_actions(self, new_actions: List[SchedulerAction]):
        """
        Add new actions to the scheduler.

        :param new_actions: A list of SchedulerAction objects to add.
        """
        for action in new_actions:
            self.actions[action.action_id] = action

    def remove_action(self, action_id: str):
        """
        Remove an action from the scheduler by its ID.

        :param action_id: The ID of the action to remove.
        """
        if action_id in self.actions:
            del self.actions[action_id]

    async def _run(self):
        """Run the actions at the specified interval."""
        while not self._stop_event.is_set():
            start_time = asyncio.get_event_loop().time()
            
            actions_to_run = list(self.actions.values())  # Get a copy of actions
            logger.info(f"SCHEDULER: Executing {len(actions_to_run)} actions.")
            for action in actions_to_run:
                try:
                    if asyncio.iscoroutinefunction(action.action_func):
                        logger.info(f"Executing action {action.action_name} {action.action_id} asynchronously.")
                        await action.action_func(**action.action_parameters)
                    else:
                        action.action_func(**action.action_parameters)
                except Exception as e:
                    logger.error(f"Error executing action {action.action_name} - {action.action_id}: {e}")
                    logger.error(traceback.format_exc())
                    
            # Calculate sleep time to maintain consistent intervals
            elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            await asyncio.sleep(sleep_time)
