from pydantic import BaseModel, Field
from typing import List, Optional
from .node import Node
import uuid
from orkestr_core.constants.providers import ProviderName
from .node_spec import NodeSpec
from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

class Cluster(BaseModel):
    """
    Represents a cluster of nodes with configurable properties and scaling capabilities.

    The cluster class is a data model and is not responsible for orchestrating the nodes.
    The orchestration is handled by the cluster orchestrator.

    All the nodes in a cluster are expected to have the same configuration.
    If a node spec is updated, the cluster will not automatically update the existing nodes.
    New nodes added to the cluster will use the updated node spec.
    The cluster will have to be restarted to update all the nodes in the cluster to the latest spec.

    Attributes:
        name (str): Name of the cluster.
        cluster_id (str): Unique identifier for the cluster.
        region (str): The region where the cluster is deployed.
        pre_booting_machines (int): Number of machines currently in the pre-booting state.
        min_nodes (int): Minimum number of nodes allowed in the cluster. Defaults to 0.
        max_nodes (int): Maximum number of nodes allowed in the cluster. Defaults to 1.
        desired_nodes (int): Desired number of nodes in the cluster. Defaults to 0.
        nodes (List[str]): List of node IDs currently in the cluster.
        _nodes (List[Node]): List of Node objects representing the nodes in the cluster. Excluded from serialization (not saved to datastore).
        node_spec_id (str): ID of the node spec used for creating nodes in the cluster.
        node_spec_version (Optional[int]): Version of the node spec used for creating nodes in the cluster.
        provider (Optional[ProviderName]): Cloud provider or infrastructure provider for the cluster.
        node_class (Type[Node]): Class type of the nodes in the cluster based on the provider. Defaults to Node.
    """

    name: str
    cluster_id: str
    region: str
    pre_booting_machines: int = 0
    min_nodes: int = 0
    max_nodes: int = 1
    desired_nodes: int = 0
    nodes: List[str] = Field(default_factory=list)
    node_spec_id: str
    node_spec_version: Optional[int] = 0
    provider: Optional[ProviderName] = None  # Use Literal with providers_list

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()
    
    def start_nodes(self, node_count, override_to_max: bool = False) -> int:
        current_node_count = len(self.nodes)
        if current_node_count + self.pre_booting_machines + node_count > self.max_nodes:
            if self.max_nodes - current_node_count - self.pre_booting_machines <= 0:
                logger.error("Cannot start more nodes, max limit reached.")
                return -1
            if not override_to_max:
                logger.error("Cannot start more nodes, max limit reached.")
                return -1
            node_count = self.max_nodes - current_node_count - self.pre_booting_machines
            
        datastore = self.get_datastore()
        self.pre_booting_machines += node_count
        datastore.save_cluster(self)
        return node_count

    def add_node(self, node_id) -> Optional[Node]:
        """
        Function to add a node to the cluster.
        """
        if len(self.nodes) < self.max_nodes:
            datastore = self.get_datastore()
           
            self.nodes.append(node_id)
            self.pre_booting_machines -= 1
            datastore.save_cluster(self)
            # The node should already be booting by now
            return node_id
        else:
            logger.error("Cannot add more nodes, max limit reached.")
            return None
    
    def add_nodes(self, num_nodes: int) -> Optional[List[Node]]:
        """
        Function to create multiple nodes based on the cluster spec and add them to the cluster.
        """
        if num_nodes <= 0:
            logger.error("Number of nodes to add must be greater than 0.")
            return []
        num_nodes = min(num_nodes, self.max_nodes - len(self.nodes))
        if len(self.nodes) + num_nodes <= self.max_nodes:
            new_nodes = []
            for _ in range(num_nodes):
                new_node = self.add_node()
                if new_node:
                    new_nodes.append(new_node)
            return new_nodes
        else:
            logger.error("Cannot add more nodes, max limit reached.")
            return None

    def remove_node(self, node_id: str) -> str:
        datastore = self.get_datastore()
        self.nodes = [nid for nid in self.nodes if nid != node_id]
        datastore.save_cluster(self)
        return node_id

    def scale(self, desired_nodes: int) -> bool:
        if self.min_nodes + self.pre_booting_machines <= desired_nodes <= self.max_nodes:
            datastore = self.get_datastore()
            self.desired_nodes = desired_nodes
            datastore.save_cluster(self)
            return True
        else:
            logger.error("Desired nodes out of bounds.")
            return False
    
    def update_node_spec(self, node_spec_id: str, version: int = None) -> None:
        datastore = self.get_datastore()
        node_spec_dict = datastore.get_node_spec(node_spec_id, self.region)
        node_spec_from_datastore = NodeSpec(**node_spec_dict)
        if not node_spec_from_datastore:
            logger.error(f"Node spec {node_spec_id} not found.")
            return
        if version is None:
            version = node_spec_from_datastore.default_version
        self.node_spec_id = node_spec_id
        self.node_spec_version = version
        datastore.save_cluster(self)