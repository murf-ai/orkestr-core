from pydantic import BaseModel
from typing import Dict, Optional
from enum import Enum
from orkestr_core.util.logger import setup_logger
from orkestr_core.constants.providers import ProviderName

logger = setup_logger(__name__)

class NodeStatus(Enum):
    IDLE = "idle"
    BOOTING = "booting"
    ACTIVE = "active"
    UNHEALTHY = "unhealthy"
    TERMINATED = "terminated"
    TERMINATING = "terminating"

class Node(BaseModel):
    """
    Base class for all nodes.

    Attributes:
        node_id (str): Unique identifier for the node.
        instance_id (Optional[str]): Instance ID of the node from the cloud provider. Use this to identify the node in the cloud.
        machine_type (str): Type of machine.
        region (str): Region where the node is located.
        disk_size (Optional[int]): Size of the disk in GB.
        user_data_script (str): User data script to run on startup.
        environment_variables (Dict[str, str]): Environment variables to set.
        status (Optional[str]): Current status of the node.
        name (Optional[str]): Name of the node.
        ip_address (Optional[str]): IP address of the node.
        provider (Optional[ProviderName]): Provider name.
        cluster_id (Optional[str]): Cluster ID where the node belongs.
        node_spec (Optional[str]): Node specification.
        node_spec_version (Optional[int]): Version of the node specification.

    """

    node_id: str
    instance_id: Optional[str] = None
    machine_type: Optional[str] = None
    region: str
    user_data_script: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
    status: Optional[str] = NodeStatus.IDLE.value
    name: Optional[str] = None
    ip_address: Optional[str] = None
    provider: Optional[ProviderName] = None
    cluster_id: str = None
    node_spec: Optional[str] = None
    node_spec_version: Optional[int] = None

    async def start(self) -> Optional[list]:
        """
        Check if the node is in an idle state before starting
        """
        if self.status == NodeStatus.IDLE.value:
            self.status = NodeStatus.BOOTING.value
        else:
            logger.warning(f"Can't start Node {self.node_id}. It is in {self.status} state.")

    async def stop(self) -> Optional[list]:
        """
        Check if the node is in an active state before stopping it.
        """
        if self.status == NodeStatus.ACTIVE.value:
            self.status = NodeStatus.TERMINATING.value
        else:
            logger.warning(f"Can't stop Node {self.node_id}. It is in {self.status} state.")
    
    def restart(self) -> None:
        """
        Restart the node
        """
        pass

    def detect_drift(self, data: dict) -> bool:
        """
        Detects drift between the desired and actual state.
        Returns True if drift is detected, False otherwise.
        """
        status = data.get("status")
        if status and status != self.status:
            logger.warning(f"Drift detected for Node {self.node_id} in cluster {self.cluster_id} - {self.provider}. Expected status: {self.status}, Actual status: {status}.")
            return True
        return False

