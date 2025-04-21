from .event import Event
from enum import Enum
from typing import ClassVar, Optional
from orkestr_core.constants.providers import OrkestrRegion

class ClusterEvent(Enum):
    SCALE_CLUSTER = "cluster.scale"
    CLUSTER_SCALE_SUCCESS = "cluster.scale.success"
    CLUSTER_SCALE_FAIL = "cluster.scale.fail"
    CLUSTER_CREATED = "cluster.created"
    CLUSTER_DELETED = "cluster.deleted"
    CLUSTER_DEGRADED = "cluster.degraded"

class ScaleClusterEvent(Event):
    """Event triggered when a cluster should be scaled"""
    event_type: ClassVar[str] = ClusterEvent.SCALE_CLUSTER.value
    cluster_id: str
    desired_nodes: int
    region: OrkestrRegion

class ClusterScaleFailedEvent(Event):
    """Event triggered when a cluster scale operation fails"""
    event_type: ClassVar[str] = ClusterEvent.CLUSTER_SCALE_FAIL.value
    cluster_id: str
    region: OrkestrRegion
    error_data: Optional[dict] = None