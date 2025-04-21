from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from .node import Node
from .node_spec import NodeSpec
from .cluster import Cluster
from .service import Service
from orkestr_core.constants.providers import OrkestrRegion

class GetAllNodesOutput(BaseModel):
    nodes: list[Node]
    count: int
    scanned_count: int
    page: int
    last_evaluated_key: Optional[dict]
    has_more: bool

class GetAllClustersOutput(BaseModel):
    clusters: list[Cluster]
    count: int
    scanned_count: int
    page: int
    last_evaluated_key: Optional[dict]
    has_more: bool
class GetAllServicesOutput(BaseModel):
    services: list[Service]
    count: int
    scanned_count: int
    page: int
    last_evaluated_key: Optional[dict]
    has_more: bool

class Datastore(ABC):
    @abstractmethod
    def save_node(self, node: Node) -> None:
        pass

    @abstractmethod
    def get_node(self, node_id: str, region: OrkestrRegion | str = None) -> Optional[Node]:
        pass

    @abstractmethod
    def get_all_nodes(self, region: OrkestrRegion | str, limit: int, page: int, last_node: Optional[dict]) -> GetAllNodesOutput:
        pass

    @abstractmethod
    def save_node_spec(self, node_spec: NodeSpec) -> None:
        pass

    @abstractmethod
    def get_node_spec(self, node_spec_id: str, region: OrkestrRegion | str = None) -> Optional[NodeSpec]:
        pass

    @abstractmethod
    def save_cluster(self, cluster: Cluster) -> None:
        pass

    @abstractmethod
    def get_cluster(self, cluster_id: str, region: OrkestrRegion | str = None) -> Optional[Cluster]:
        pass

    @abstractmethod
    def get_all_clusters(self, region: OrkestrRegion | str, limit: int, page: int, last_cluster: Optional[dict]) -> GetAllClustersOutput:
        pass

    @abstractmethod
    def save_service(self, service: Service) -> None:
        pass

    @abstractmethod
    def get_service(self, service_id: str) -> Optional[Service]:
        pass

    @abstractmethod
    def get_all_services(self, limit: int, page: int, last_service: Optional[dict]) -> GetAllServicesOutput:
        pass