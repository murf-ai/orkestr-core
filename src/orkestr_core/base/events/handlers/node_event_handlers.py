from orkestr_core.base.events import AsyncEventBus
from orkestr_core.base.events.event_library import StartNodeEvent, StartMultipleNodes, NodeStartedEvent, TerminateNodeEvent, NodeDriftDetectedEvent, TerminateMultipleNodes
from orkestr_core.base.orchestrator.node_orchestrator import NodeOrchestrator
from orkestr_core.util.logger import setup_logger
from orkestr_core.base.node import NodeStatus

logger = setup_logger(__name__)

class NodeEventHandler:
    def __init__(self, event_bus: AsyncEventBus, orchestrator: NodeOrchestrator):
        self.event_bus = event_bus
        self.orchestrator = orchestrator

    def register_event_handlers(self):
        self.event_bus.subscribe_to_event(
            StartNodeEvent,
            self.handle_start_node
        )
        self.event_bus.subscribe_to_event(
            StartMultipleNodes,
            self.handle_start_multiple_nodes
        )
        self.event_bus.subscribe_to_event(
            TerminateNodeEvent,
            self.handle_terminate_node
        )
        self.event_bus.subscribe_to_event(
            TerminateMultipleNodes,
            self.handle_terminate_multiple_nodes
        )
        self.event_bus.subscribe_to_event(
            NodeDriftDetectedEvent,
            self.handle_node_drift
        )
        self.event_bus.subscribe_to_event(
            NodeStartedEvent,
            self.handle_node_started
        )
    
    async def handle_start_node(self, event: StartNodeEvent):
        node_id = event.node_id
        region = event.region
        if node_id:
            await self.orchestrator.start_node(node_id, region=region)
        else:
            logger.error("Node ID is required to start the node.")

    async def handle_start_multiple_nodes(self, event: StartMultipleNodes):
        count = event.count
        cluster_id = event.cluster_id
        region = event.region
        if count > 0:
            await self.orchestrator.start_nodes(count, cluster_id, region)
        else:
            logger.error("Count must be greater than zero to start multiple nodes.")

    async def handle_node_started(self, event: NodeStartedEvent):
        node_id = event.node_id
        region = event.region
        if node_id:
            await self.orchestrator.update_node(node_id, new_data={'status': NodeStatus.ACTIVE}, region=region)
        else:
            logger.error("Node ID is required to add the node.")
    
    async def handle_terminate_node(self, event: TerminateNodeEvent):
        node_id = event.node_id
        region = event.region
        if node_id:
            await self.orchestrator.terminate_node(node_id, region)
        else:
            logger.error("Node ID is required to terminate the node.")

    async def handle_terminate_multiple_nodes(self, event: TerminateMultipleNodes):
        count = event.count
        cluster_id = event.cluster_id
        region = event.region
        if count > 0:
            await self.orchestrator.terminate_nodes(count, cluster_id, region)
        else:
            logger.error("Count must be greater than zero to terminate multiple nodes.")

    async def handle_node_drift(self, event: NodeDriftDetectedEvent):
        orkestr_node = event.orkestr_node
        drifted_node = event.drifted_node

        if orkestr_node and drifted_node:
            await self.orchestrator.resolve_drift(orkestr_node, drifted_node)
        else:
            logger.error("Orkestr node and drifted node are required to resolve drift.")