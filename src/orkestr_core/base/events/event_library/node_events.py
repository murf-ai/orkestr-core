from .event import Event
from enum import Enum
from typing import ClassVar, Optional
from orkestr_core.constants.providers import OrkestrRegion

class NodeEvent(Enum):
    START_NODE = "node.start"
    START_MULTIPLE_NODES = "node.start_multiple"
    NODE_BOOTING = "node.booting"
    NODE_STARTED = "node.started"
    TERMINATE_NODE = "node.terminate"
    TERMINATE_MULTIPLE_NODES = "node.terminate_multiple"
    NODE_DRIFT_DETECTED = "node.drift_detected"
    NODE_UNHEALTHY = "node.unhealthy"
    NODE_TERMINATED = "node.terminated"

class StartNodeEvent(Event):
    """Event triggered when a node should be started"""
    event_type: ClassVar[str] = NodeEvent.START_NODE.value
    node_id: str
    region: OrkestrRegion

class StartMultipleNodes(Event):
    """Event triggered when multiple nodes should be started"""
    event_type: ClassVar[str] = NodeEvent.START_MULTIPLE_NODES.value
    cluster_id: str
    count: int
    region: OrkestrRegion

class NodeBootingEvent(Event):
    """Event triggered when a node is booting"""
    event_type: ClassVar[str] = NodeEvent.NODE_BOOTING.value
    node_id: str
    cluster_id: str
    region: OrkestrRegion

class NodeStartedEvent(Event):
    """Event triggered when a node has started successfully"""
    event_type: ClassVar[str] = NodeEvent.NODE_STARTED.value
    node_id: str
    cluster_id: str
    region: OrkestrRegion
    instances: Optional[list] = []

class TerminateNodeEvent(Event):
    """Event triggered when a node should be terminated"""
    event_type: ClassVar[str] = NodeEvent.TERMINATE_NODE.value
    node_id: str
    region: OrkestrRegion

class TerminateMultipleNodes(Event):
    """Event triggered when multiple nodes should be terminated"""
    event_type: ClassVar[str] = NodeEvent.TERMINATE_MULTIPLE_NODES.value
    cluster_id: str
    count: int
    region: OrkestrRegion

class NodeTerminatedEvent(Event):
    """Event triggered when a node has been terminated"""
    event_type: ClassVar[str] = NodeEvent.NODE_TERMINATED.value
    node_id: str
    cluster_id: str
    region: OrkestrRegion
    instance: Optional[str] = None

class NodeDriftDetectedEvent(Event):
    """Event triggered when a node drift is detected"""
    event_type: ClassVar[str] = NodeEvent.NODE_DRIFT_DETECTED.value
    orkestr_node: dict
    drifted_node: dict

class NodeUnhealthyEvent(Event):
    """Event triggered when a node is detected as unhealthy"""
    event_type: ClassVar[str] = NodeEvent.NODE_UNHEALTHY.value
    node_id: str
    region: OrkestrRegion
    cluster_id: str