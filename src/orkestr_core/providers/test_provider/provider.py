from orkestr_core.base.provider import Provider
from orkestr_core.constants.providers import OrkestrRegion
from .test_provider_client import TestProviderClient, TestProviderAsyncClient
from .base.test_node import TestNode
from orkestr_core.base.drift_detector import detect_node_drift
from orkestr_core.util.logger import setup_logger
from orkestr_core.base.events.event_library import NodeDriftDetectedEvent

logger = setup_logger(__name__)

class TestProvider(Provider):
    node_class = TestNode

    def __init__(self, event_bus=None):
        self.client = TestProviderClient()
        self.async_client = TestProviderAsyncClient()
        self.event_bus = event_bus

    def check_and_sync_infra(self, regions = ...):
        return super().check_and_sync_infra(regions)

    async def acheck_and_sync_infra(self, regions: list[OrkestrRegion] = []):
        logger.info("Asynchronously checking and syncing infrastructure for TestProvider.")
        from orkestr_core.datastores.global_datastore import get_global_datastore
        datastore = get_global_datastore()
        all_provider_nodes = await self.async_client.list_instances()
        all_provider_nodes_dict: dict = {
            node["instance_id"]: node for node in all_provider_nodes
        }
        all_nodes: list[TestNode] = []
        for region in regions:
            has_more = True
            page = 1
            limit = 100
            last_node = None
            while has_more:
                filters = {
                    "region": region.value
                }
                logger.info(f"Fetching nodes for region {region.value} with filters: {filters}")
                nodes_res = datastore.get_all_nodes(region=region, limit=limit, page=page, last_node=last_node, filters=filters)
                all_nodes.extend(nodes_res.nodes)
                has_more = nodes_res.has_more
                page += 1
                if 'last_evaluated_key' in nodes_res:
                    last_node = nodes_res.last_evaluated_key

        for node in all_nodes:
            # find the node using the instance_id
            if node.instance_id in all_provider_nodes_dict:
                is_drifting = detect_node_drift(node, all_provider_nodes_dict[node.instance_id])
                if is_drifting:
                    self.event_bus.emit(
                        NodeDriftDetectedEvent(
                            orkestr_node=node,
                            drifted_node=all_provider_nodes_dict[node.instance_id]
                        )
                    )