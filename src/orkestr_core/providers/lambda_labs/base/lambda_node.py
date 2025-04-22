from orkestr_core.base.node import Node, NodeStatus
from orkestr_core.base.node_spec import NodeSpec, NodeSpecConfiguration
from orkestr_core.constants.providers import ProviderName, OrkestrRegion, RegionMapper
from orkestr_core.providers.lambda_labs.lambda_labs_client import LambdaLabsAsyncClient
from orkestr_core.util.logger import setup_logger
from typing import Optional

logger = setup_logger(__name__)

lambda_labs_client = LambdaLabsAsyncClient()

class LambdaNode(Node):
    provider: ProviderName = ProviderName.LAMBDA_LABS
    ssh_key_names: Optional[list[str]] = ["orkestr-ssh-key"]

    def get_datastore(self):
        from orkestr_core.datastores.global_datastore import get_global_datastore
        return get_global_datastore()

    async def start(self) -> Optional[str]:
        new_instances = None
        try:
            if self.status == NodeStatus.IDLE.value:
                self.status = NodeStatus.BOOTING.value
            else:
                logger.warning(f"Can't start Node {self.node_id}. It is in {self.status} state.")
                return None
            datastore = self.get_datastore()
            region = RegionMapper.get_provider_region(orkestr_region=OrkestrRegion[self.region], provider=self.provider)
            node_spec_dict = datastore.get_node_spec(self.node_spec, self.region)
            node_spec = NodeSpec(**node_spec_dict)
            node_spec_config: NodeSpecConfiguration = node_spec.versions[self.node_spec_version]
            machine_type = node_spec_config.machine_type
            user_data_script = None
            try:
                user_data_script = node_spec_config.user_data_script
                logger.info("User data script found for node spec version {self.node_spec_version} in {node_spec}: {user_data_script}.")
            except Exception as e:
                logger.error(f"Node spec version {self.node_spec_version} not found for node {self.node_id} in {node_spec}.")
                return None
            node_name = self.name or self.node_id
            res = await lambda_labs_client.launch_instance(
                name=node_name,
                region_name=region,
                instance_type_name=machine_type,
                ssh_key_names=self.ssh_key_names,
                user_data_script=user_data_script
            )
            res_data = res.get("data")
            new_instances = res_data.get("instance_ids")
            if new_instances:
                self.instance_id = new_instances[0]
                self.machine_type = machine_type
                self.status = NodeStatus.BOOTING.value
                datastore.save_node(self)
            else:
                logger.error(f"Failed to start node {self.node_id}. No instances returned.")
                return None
            
        except Exception as e:
            self.status = "unhealthy"
            return None
        return new_instances[0] if new_instances else None
        
    async def stop(self) -> Optional[str]:
        terminated_instances = None
        try:
            if self.status == NodeStatus.TERMINATED.value or self.status == NodeStatus.TERMINATING.value:
                logger.error(f"Can't stop Node {self.node_id}. It is in {self.status} state.")
                return
            datastore = self.get_datastore()
            res = await lambda_labs_client.terminate_instances([self.instance_id])
            res_data = res.get("data")
            terminated_instances = res_data.get("terminated_instances")
            if terminated_instances and terminated_instances[0].get("status") in [NodeStatus.TERMINATED.value, NodeStatus.TERMINATING.value]:
                self.status = terminated_instances[0].get("status")
            else:
                return None
            datastore.save_node(self)
        except Exception as e:
            self.status = NodeStatus.UNHEALTHY.value
            raise e
        return terminated_instances[0] if terminated_instances else None