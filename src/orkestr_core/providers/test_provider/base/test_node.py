from orkestr_core.base.node import Node, NodeStatus
from orkestr_core.base.node_spec import NodeSpec, NodeSpecConfiguration
from orkestr_core.constants.providers import ProviderName
from orkestr_core.providers.test_provider.test_provider_client import TestProviderAsyncClient
from orkestr_core.base.provider_client import ProviderClient
from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

test_provider_client = TestProviderAsyncClient()

class TestNode(Node):
    provider: ProviderName = ProviderName.TEST_PROVIDER

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()
        
    async def start(self) -> bool:
        try:
            logger.info(f"Starting node {self.node_id} in region {self.region}.")
            # Ensure the node is in a state where it can be started
            if self.status != NodeStatus.IDLE.value:
                logger.warning(f"Can't start Node {self.node_id}. It is in {self.status} state.")
                return
            datastore = self.get_datastore()
            node_spec_dict = datastore.get_node_spec(self.node_spec, self.region)
            node_spec = NodeSpec(**node_spec_dict)
            node_spec_config: NodeSpecConfiguration = node_spec.versions[self.node_spec_version]
            machine_type = node_spec_config.machine_type
            user_data_script = None
            try:
                user_data_script = node_spec_config.user_data_script
                logger.info(f"User data script found for node spec version {self.node_spec_version} in {node_spec}: {user_data_script}.")
            except Exception as e:
                logger.error(f"Node spec version {self.node_spec_version} not found for node {self.node_id} in {node_spec}.")
                raise e
            new_instances = None
            res = await test_provider_client.launch_instance(
                region_name=self.region,
                instance_type_name=machine_type,
                ssh_key_names=[],
                name=self.name,
                node_id=self.node_id,
                user_data_script=user_data_script,
            )
            new_instances = res.get("instance_id")
            if new_instances:
                self.instance_id = new_instances
                self.status = NodeStatus.BOOTING.value
                logger.info(f"Node {self.node_id} with instance id {self.instance_id} is now booting")
                datastore.save_node(self)
            else:
                logger.error(f"Failed to start node {self.node_id}. No instances returned.")
                return None
        except Exception as e:
            self.status = NodeStatus.UNHEALTHY.value
            raise e
        
        return new_instances or None

    async def stop(self):
        terminated_instances = None
        try:
            if self.status == NodeStatus.TERMINATED.value or self.status == NodeStatus.TERMINATING.value:
                logger.error(f"Can't stop Node {self.node_id}. It is in {self.status} state.")
                return
            datastore = self.get_datastore()
            res = await test_provider_client.terminate_instances([self.instance_id])
            terminated_instances = res.get("terminated_instance_ids")
            if terminated_instances and self.instance_id in terminated_instances:
                self.status = NodeStatus.TERMINATED.value
            else:
                return None
            datastore.save_node(self)
        except Exception as e:
            self.status = NodeStatus.UNHEALTHY.value
            raise e
        return terminated_instances[0] if terminated_instances else None