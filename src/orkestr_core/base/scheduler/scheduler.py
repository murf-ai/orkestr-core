import threading
import time
from typing import List
from .scheduler_action import SchedulerAction  # Ensure correct import

class Scheduler:
    def __init__(self, actions: List[SchedulerAction], interval: float):
        """
        Initialize the Scheduler.

        :param actions: A list of SchedulerAction objects to execute.
        :param interval: Time interval (in seconds) between each execution.
        """
        self.actions = {action.action_id: action for action in actions}  # Store actions by ID
        self.interval = interval
        self._stop_event = threading.Event()
        self._lock = threading.Lock()  # Lock for thread-safe access to actions
        self._thread = None  # Initialize as None, will be created in start()

    def start(self):
        """Start the scheduler in a separate thread."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._stop_event.clear()
        self._thread.start()


    def stop(self):
        """Stop the scheduler."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self._thread = None  # Reset the thread after stopping

    def add_actions(self, new_actions: List[SchedulerAction]):
        """
        Add new actions to the scheduler.

        :param new_actions: A list of SchedulerAction objects to add.
        """
        with self._lock:
            for action in new_actions:
                self.actions[action.action_id] = action
    
    def remove_action(self, action_id: str):
        """
        Remove an action from the scheduler by its ID.

        :param action_id: The ID of the action to remove.
        """
        with self._lock:
            if action_id in self.actions:
                del self.actions[action_id]


    def _run(self):
        """Run the actions at the specified interval."""
        while not self._stop_event.is_set():
            start_time = time.time()
            with self._lock:
                actions_to_run = list(self.actions.values())  # Get a copy of actions
                
            for action in actions_to_run:
                try:
                    action.execute()  # Call the execute method
                except Exception as e:
                    print(f"Error executing action {action.action_id}: {e}")
                    
            # Calculate sleep time to maintain consistent intervals
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)
