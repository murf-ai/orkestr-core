from abc import ABC, abstractmethod
from typing import Type
from orkestr_core.base.node import Node
from orkestr_core.base.cluster import Cluster

class ProviderClient(ABC):
    api_key: str
    base_url: str
    
    @abstractmethod
    def launch_instance(self, **kwargs):
        """
        Launches a new instance.
        """
        pass

    @abstractmethod
    def terminate_instances(self, instance_ids: list):
        """
        Terminates one or more instances.
        """
        pass

    @abstractmethod
    def list_instances(self):
        """
        Lists all running instances.
        """
        pass

    @abstractmethod
    def get_instance_details(self, instance_id: str):
        """
        Retrieves details of a specific instance.
        """
        pass

    @abstractmethod
    def list_instance_types(self):
        """
        Lists all available instance types.
        """
        pass
