from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from orkestr_core.base.cluster import Cluster

class ClusterConfiguration(BaseModel):
    cluster_id: str
    region: str
    weight: int
    deployment_group: Optional[str] = None

class Service(BaseModel):
    """
    Service class to manage clusters and their configurations.

    Attributes:
        name (str): Name of the service.
        service_id (str): Unique identifier for the service.
        clusters (List[ClusterConfiguration]): List of cluster configurations associated with the service.
        max_nodes (int): Maximum number of nodes allowed in the service. Defaults to 1.
        min_nodes (int): Minimum number of nodes allowed in the service. Defaults to 0.
        desired_nodes (int): Desired number of nodes in the service. Defaults to 0.
        _clusters (List[Cluster]): List of Cluster objects representing the clusters in the service. Excluded from serialization (not saved to datastore).
    """
    name: str
    service_id: str
    clusters: List[ClusterConfiguration] = Field(default_factory=list)
    internal_clusters: List[Cluster] = Field(default_factory=list, exclude=True)
    max_nodes: int = 1
    min_nodes: int = 0
    desired_nodes: int = 0

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()

    def add_cluster(self, cluster_id: str, region, weight: int = 1, deployment_group: str = None) -> None:
        """
        Function to add a cluster to the service.
        A cluster is expected to be already created before adding it to the service.
        """
        self.clusters.append(ClusterConfiguration(cluster_id=cluster_id, weight=weight, deployment_group=deployment_group, region=region))
        datastore = self.get_datastore()
        datastore.save_service(self)

    def add_internal_cluster(self, cluster: Cluster) -> None:  
        self.internal_clusters.append(cluster)
        
    def set_internal_clusters(self, clusters: List[Cluster]) -> None:
        self.internal_clusters = clusters

    def remove_cluster(self, cluster_id: str) -> None:
        self.clusters = [cluster for cluster in self.clusters if cluster.cluster_id != cluster_id]
        datastore = self.get_datastore()
        datastore.save_service(self)

    def scale_service(self):
        """
        Function to scale the service based on the weights of the clusters.
        """
        datastore = self.get_datastore()

        total_weight = sum([cluster.weight for cluster in self.clusters])

        allocated_nodes = 0
        cluster_sizes = []

        for i, service_cluster in enumerate(self.clusters):
            cluster = datastore.get_cluster(service_cluster.cluster_id, service_cluster.region)
            if cluster is None:
                raise Exception("Cluster not found in the datastore")
            
            if i == len(self.clusters) - 1:
                # Assign remaining nodes to the last cluster to ensure the total matches desired_nodes
                cluster_size = self.desired_nodes - allocated_nodes
            else:
                cluster_size = round((service_cluster.weight / total_weight) * self.desired_nodes)
                allocated_nodes += cluster_size
            
            cluster_size = min(cluster_size, cluster.max_nodes)
            cluster_size = max(cluster_size, cluster.min_nodes)
            cluster_sizes.append((cluster, cluster_size))

        for cluster, cluster_size in cluster_sizes:
            cluster.scale(cluster_size)

        datastore.save_service(self)