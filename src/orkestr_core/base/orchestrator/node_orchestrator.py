from orkestr_core.util.logger import setup_logger
# from orkestr_core.providers.provider_registry import ProviderRegistry
from orkestr_core.base.events import AsyncEventBus
from orkestr_core.base.events.event_library import NodeBootingEvent, NodeStartedEvent, NodeTerminatedEvent, ClusterScaleFailedEvent, NodeUnhealthyEvent
from orkestr_core.base.node import NodeStatus
from orkestr_core.constants.providers import OrkestrRegion
import uuid

logger = setup_logger(__name__)

class NodeOrchestrator:
    def __init__(self, event_bus: AsyncEventBus, provider_registry):
        self.event_bus = event_bus
        self.provider_registry = provider_registry

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()

    async def start_node(self, cluster_id: str, region: OrkestrRegion):
        logger.info(f"INITIATING NODE START from NODE ORCHESTRATOR in cluster {cluster_id} in region {region}.") 
        datastore = self.get_datastore()
        cluster = datastore.get_cluster(cluster_id, region=region)
        cluster_name = cluster["name"]
        node_provider = cluster["provider"]
        provider_class = self.provider_registry.get_provider(node_provider)
        node_class = provider_class.node_class
        node_id = f"{cluster_name}-node-{uuid.uuid4()}"
        node_instance = node_class(
            name=node_id,
            node_id=node_id,
            cluster_id=cluster_id,
            region=region,
            status = NodeStatus.IDLE.value,
            provider = node_provider,
            node_spec = cluster["node_spec_id"],
            node_spec_version = cluster["node_spec_version"],
        )
        node_region = cluster["region"]
        try:
            new_instance = await node_instance.start()
            if not new_instance:
                self.event_bus.emit(
                    ClusterScaleFailedEvent(
                        node_id=node_id,
                        cluster_id=cluster_id,
                        region=OrkestrRegion[node_region]
                    )
                )
                logger.error(f"Node Orchestrator: Failed to start node {node_id}. No instances returned.")
                return
            self.event_bus.emit(
                NodeBootingEvent(
                    node_id=node_id,
                    cluster_id=cluster_id,
                    instances=[new_instance],
                    region=OrkestrRegion[node_region]
                )
            )
            logger.info(f"Node Orchestrator: Node {node_id} with instance id {new_instance} is now booting")
        except Exception as e:
            logger.error(f"Failed to start node {node_id}: {e}")
    
    async def start_nodes(self, count: int, cluster_id: str, region: OrkestrRegion):
        for i in range(count):
            await self.start_node(cluster_id=cluster_id, region=region)
        
    async def terminate_node(self, node_id: str, region: OrkestrRegion):
        datastore = self.get_datastore()
        node = datastore.get_node(node_id, region=region)
        node_provider = node["provider"]
        provider_class = self.provider_registry.get_provider(node_provider)
        node_class = provider_class.node_class
        node_instance = node_class(**node)
        node_region = node["region"]
        try:
            terminated_instance = await node_instance.stop()
            if not terminated_instance:
                logger.error(f"Failed to stop node {node_id}. No instances returned.")
                return
            self.event_bus.emit(
                NodeTerminatedEvent(
                    node_id=node_id,
                    cluster_id=node["cluster_id"],
                    region=node_region,
                    instance=node["instance_id"]
                )
            )
            logger.info(f"Node {node_id} stopped successfully.")
        except Exception as e:
            logger.error(f"Failed to stop node {node_id}: {e}")

    async def terminate_nodes(self, count: int, cluster_id: str, region: OrkestrRegion):
        datastore = self.get_datastore()
        cluster = datastore.get_cluster(cluster_id, region=region)
        cluster_nodes = cluster["nodes"]
        if count > len(cluster_nodes):
            logger.error(f"Cannot terminate {count} nodes. Only {len(cluster_nodes)} nodes available.")
            return
        nodes_to_terminate = cluster_nodes[:count]
        for node in nodes_to_terminate:
            await self.terminate_node(node_id=node["node_id"], region=region)

    
    async def resolve_drift(self, orkestr_node: dict, drifted_node: dict) -> None:
        """
        Resolves the detected drift by reconciling the actual state with the desired state.
        """
        node_id = orkestr_node.get("node_id")
        status = drifted_node.get("status")
        region = OrkestrRegion[orkestr_node.get("region")]
        logger.info(f"Resolving drift for Node {node_id} - with status {status} - in region {region}.")
        
        if status in [NodeStatus.IDLE.value, NodeStatus.BOOTING.value]:
            # do nothing
            logger.info("Node is either IDLE or BOOTING. No action required.")
            pass
        elif status in [NodeStatus.ACTIVE.value, NodeStatus.UNHEALTHY.value, NodeStatus.TERMINATED.value, NodeStatus.TERMINATING.value]:
            if status == NodeStatus.UNHEALTHY.value:
                self.event_bus.emit(NodeUnhealthyEvent(node_id=node_id, cluster_id=orkestr_node.get("cluster_id"), region=region))
            elif status == NodeStatus.TERMINATED.value or status == NodeStatus.TERMINATING.value:
                self.event_bus.emit(NodeTerminatedEvent(node_id=node_id, cluster_id=orkestr_node.get("cluster_id"), region=region))
            elif status == NodeStatus.ACTIVE.value:
                self.event_bus.emit(NodeStartedEvent(node_id=node_id, cluster_id=orkestr_node.get("cluster_id"), region=region))
        else:
            logger.warning(f"Can't resolve drift for Node {node_id}. Invalid status {status}.")
            return
        self.status = status
        
    async def update_node(self, node_id: str, new_data: dict, region: OrkestrRegion):
        datastore = self.get_datastore()
        node = datastore.get_node(node_id, region=region)
        node_provider = node["provider"]
        provider_class = self.provider_registry.get_provider(node_provider)
        node_class = provider_class.node_class
        merged_data = {
            **node,
            **new_data
        }
        node_instance = node_class(
            **merged_data
        )
        logger.info(f"Updating node {node_id} with new data: {new_data}.")
        datastore.save_node(node_instance)