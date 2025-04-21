from abc import ABC, abstractmethod
from typing import Type, Optional
from orkestr_core.base.node import Node
from orkestr_core.base.cluster import Cluster
from orkestr_core.base.provider_client import ProviderClient
from orkestr_core.base.events import AsyncEventBus

class Provider(ABC):
    node_class: Type[Node]
    client: ProviderClient
    async_client: ProviderClient
    event_bus: Optional[AsyncEventBus] = None

    def create_node(self, node_data: dict) -> Node:
        """
        Creates a new node instance based on the provider-specific Node class.
        """
        return self.node_class(**node_data)

    @abstractmethod
    def check_and_sync_infra(self, regions: list[str] = []):
        """
        Retrieves the state of all the nodes in the provider and updates the internal infra state.
        """
        pass

    @abstractmethod
    async def acheck_and_sync_infra(self, regions: list[str] = []):
        """
        Asynchronously retrieves the state of all the nodes in the provider and updates the internal infra state.
        """
        pass
