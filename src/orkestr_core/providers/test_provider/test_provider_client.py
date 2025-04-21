from orkestr_core.base.provider_client import ProviderClient
import asyncio

class TestProviderClient(ProviderClient):
    def __init__(self, api_key: str = "test_api_key", base_url: str = "http://test-provider.local"):
        self.api_key = api_key
        self.base_url = base_url

    def launch_instance(self, **kwargs):
        """
        Returns dummy data for launching an instance.
        """
        return {"instance_id": "test-instance-123", "status": "launched"}
        # return {}

    def terminate_instances(self, instance_ids: list):
        """
        Returns dummy data for terminating instances.
        """
        return {"terminated_instance_ids": instance_ids, "status": "terminated"}

    def list_instances(self):
        """
        Returns dummy data for listing instances.
        """
        return [
            {"instance_id": "test-instance-123", "status": "running"},
            {"instance_id": "test-instance-456", "status": "stopped"},
        ]

    def get_instance_details(self, instance_id: str):
        """
        Returns dummy data for instance details.
        """
        return {"instance_id": instance_id, "status": "running", "type": "test-type"}

    def list_instance_types(self):
        """
        Returns dummy data for instance types.
        """
        return [
            {"type": "test-type-1", "description": "Test instance type 1"},
            {"type": "test-type-2", "description": "Test instance type 2"},
        ]

class TestProviderAsyncClient(ProviderClient):
    def __init__(self, api_key: str = "test_api_key", base_url: str = "http://test-provider.local"):
        self.api_key = api_key
        self.base_url = base_url

    async def launch_instance(self, **kwargs):
        """
        Returns dummy data for launching an instance asynchronously.
        """
        await asyncio.sleep(0.1)
        instance_id = kwargs.get("node_id", "test-instance-123")
        instance_id += "-instance"
        return {"instance_id": instance_id, "status": "launched"}
        # return {}

    async def terminate_instances(self, instance_ids: list):
        """
        Returns dummy data for terminating instances asynchronously.
        """
        await asyncio.sleep(0.1)
        return {"terminated_instance_ids": instance_ids, "status": "terminated"}

    async def list_instances(self):
        """
        Returns dummy data for listing instances asynchronously.
        """
        await asyncio.sleep(0.1)
        return [
            {"instance_id": "test-instance-123", "status": "running"},
            {"instance_id": "test-instance-456", "status": "stopped"},
        ]

    async def get_instance_details(self, instance_id: str):
        """
        Returns dummy data for instance details asynchronously.
        """
        await asyncio.sleep(0.1)
        return {"instance_id": instance_id, "status": "running", "type": "test-type"}

    async def list_instance_types(self):
        """
        Returns dummy data for instance types asynchronously.
        """
        await asyncio.sleep(0.1)
        return [
            {"type": "test-type-1", "description": "Test instance type 1"},
            {"type": "test-type-2", "description": "Test instance type 2"},
        ]

