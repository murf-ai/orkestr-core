from orkestr_core.util.logger import setup_logger
from orkestr_core.base.cluster import Cluster
from orkestr_core.base.node import Node
# from orkestr_core.providers.provider_registry import ProviderRegistry
from orkestr_core.base.events import AsyncEventBus
from orkestr_core.base.events.event_library import StartNodeEvent, TerminateNodeEvent, StartMultipleNodes
from orkestr_core.constants.providers import OrkestrRegion

logger = setup_logger(__name__)

class ClusterOrchestrator:
    def __init__(self, event_bus: AsyncEventBus,  provider_registry):
        self.event_bus = event_bus
        self.provider_registry = provider_registry

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()

    def add_node(self, cluster_id: str, node_id: str, region: OrkestrRegion):
        datastore = self.get_datastore()
        cluster_data = datastore.get_cluster(cluster_id, region=region)
        cluster = Cluster(**cluster_data)
        if node_id in cluster.nodes:
            logger.error(f"Node {node_id} already exists in cluster {cluster_id}.")
            return
        new_node = cluster.add_node(node_id)
        if new_node:
            logger.info(f"Node {node_id} added to cluster {cluster_id}.")
        else:
            logger.error(f"Failed to add node to cluster {cluster_id}.")

    def scale(self, cluster_id: str, region: OrkestrRegion, desired_nodes: int):
        datastore = self.get_datastore()
        cluster_data = datastore.get_cluster(cluster_id, region)
        cluster = Cluster(**cluster_data)
        can_cluster_scale = cluster.scale(desired_nodes)
        if not can_cluster_scale:
            logger.error(f"Cluster {cluster_id} cannot scale to {desired_nodes} nodes.")
            return
        # Redundant check for min and max nodes
        if desired_nodes > cluster.max_nodes:
            logger.error(f"Desired nodes {desired_nodes} exceed max nodes {cluster.max_nodes} for cluster {cluster_id}.")
            return
        if desired_nodes < cluster.min_nodes:
            logger.error(f"Desired nodes {desired_nodes} less than min nodes {cluster.min_nodes} for cluster {cluster_id}.")
            return

        if desired_nodes > len(cluster.nodes):
            start_nodes_count = desired_nodes - len(cluster.nodes)
            new_nodes_count = cluster.start_nodes(start_nodes_count, override_to_max=True)
            if new_nodes_count > 0:
                logger.info(f"Pre booting {new_nodes_count} nodes to cluster {cluster_id}.")
                self.event_bus.emit(
                    StartMultipleNodes(
                        count=new_nodes_count,
                        cluster_id=cluster_id,
                        region=region
                    )
                )
            else:
                logger.error(f"Failed to add nodes to cluster {cluster_id}.")
        elif desired_nodes < len(cluster.nodes):
            no_of_nodes_to_remove = len(cluster.nodes) - desired_nodes
            logger.info(f"Removing {no_of_nodes_to_remove} nodes from cluster {cluster_id}.")
            for node in cluster.nodes[desired_nodes:]:
                self.event_bus.emit(
                    TerminateNodeEvent(
                        node_id=node,
                        region=cluster.region
                    )
                )
            logger.info(f"Initiated termination of {no_of_nodes_to_remove} nodes in cluster {cluster_id}.")
        logger.info(f"Initiated cluster scale for {cluster_id} to {desired_nodes} nodes.")

    def remove_node(self, cluster_id: str, node_id: str, region: OrkestrRegion):
        datastore = self.get_datastore()
        cluster_data = datastore.get_cluster(cluster_id, region=region)
        cluster = Cluster(**cluster_data)
        cluster.remove_node(node_id)
        self.scale(
            cluster_id=cluster_id,
            region=region,
            desired_nodes=cluster.desired_nodes
        )
        logger.info(f"Node {node_id} removed from cluster {cluster_id}.")

    def handle_unhealthy_node(self, cluster_id: str, node_id: str, region: OrkestrRegion):
        datastore = self.get_datastore()
        cluster_data = datastore.get_cluster(cluster_id, region=region)
        cluster = Cluster(**cluster_data)
        cluster.remove_node(node_id)
        self.event_bus.emit(
            TerminateNodeEvent(
                node_id=node_id,
                region=cluster.region
            )
        )
        logger.info(f"Unhealthy node {node_id} terminated and removed from cluster {cluster_id}.")
        self.scale(
            cluster_id=cluster_id,
            region=region,
            desired_nodes=cluster.desired_nodes
        )

    def handle_cluster_scale_failed(self, cluster_id: str, region: OrkestrRegion, error_data: dict):
        logger.error(f"Cluster {cluster_id} in region {region.value} scale failed with error: {error_data}")
        datastore = self.get_datastore()
        cluster_data = datastore.get_cluster(cluster_id, region=region)
        cluster = Cluster(**cluster_data)
        cluster.pre_booting_machines = max(0, cluster.pre_booting_machines - 1)
        datastore.save_cluster(cluster)
        # @TODO: Implement retry logic or alerting mechanism
        