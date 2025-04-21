from orkestr_core.base.events import AsyncEventBus
from orkestr_core.base.events.event_library import NodeUnhealthyEvent, ScaleClusterEvent, NodeBootingEvent, ClusterScaleFailedEvent, NodeTerminatedEvent
from orkestr_core.base.orchestrator.cluster_orchestrator import ClusterOrchestrator

class ClusterEventHandler:
    def __init__(self, event_bus: AsyncEventBus, orchestrator: ClusterOrchestrator):
        self.event_bus = event_bus
        self.orchestrator = orchestrator

    def register_event_handlers(self):
        self.event_bus.subscribe_to_event(
            ScaleClusterEvent,
            self.handle_scale_event
        )
        self.event_bus.subscribe_to_event(
            NodeUnhealthyEvent,
            self.handle_unhealthy_node_event
        )
        self.event_bus.subscribe_to_event(
            NodeBootingEvent,
            self.handle_node_booting_event
        )
        self.event_bus.subscribe_to_event(
            ClusterScaleFailedEvent,
            self.handle_cluster_scale_failed_event
        )
        self.event_bus.subscribe_to_event(
            NodeTerminatedEvent,
            self.handle_node_terminated_event
        )

    async def handle_scale_event(self, event: ScaleClusterEvent):
        cluster_id = event.cluster_id
        desired_nodes = event.desired_nodes
        region = event.region
        if cluster_id and desired_nodes is not None:
            self.orchestrator.scale(cluster_id, desired_nodes=desired_nodes, region=region)

    async def handle_node_booting_event(self, event: NodeBootingEvent):
        cluster_id = event.cluster_id
        node_id = event.node_id
        region = event.region
        if cluster_id and node_id:
            self.orchestrator.add_node(cluster_id=cluster_id, node_id=node_id, region=region)


    async def handle_unhealthy_node_event(self, event: NodeUnhealthyEvent):
        cluster_id = event.cluster_id
        region = event.region
        node_id = event.node_id
        if cluster_id and node_id:
            self.orchestrator.handle_unhealthy_node(cluster_id, node_id, region=region)

    async def handle_node_terminated_event(self, event: NodeTerminatedEvent):
        cluster_id = event.cluster_id
        node_id = event.node_id
        region = event.region
        if cluster_id and node_id:
            self.orchestrator.remove_node(cluster_id=cluster_id, node_id=node_id, region=region)

    async def handle_cluster_scale_failed_event(self, event: ClusterScaleFailedEvent):
        cluster_id = event.cluster_id
        region = event.region
        error_data = event.error_data
        if cluster_id:
            self.orchestrator.handle_cluster_scale_failed(cluster_id, region=region, error_data=error_data)