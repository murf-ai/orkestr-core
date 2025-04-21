import os
from orkestr_core.base.provider_client import ProviderClient
import httpx
from dotenv import load_dotenv
from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

class LambdaLabsClient(ProviderClient):
    def __init__(self, api_key: str = os.getenv("LAMBDA_API_KEY") , base_url: str = "https://cloud.lambdalabs.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def launch_instance(self, region_name: str, instance_type_name: str, ssh_key_names: list, name: str = None, file_system_names: list = None):
        """
        Launches a new instance.
        """
        url = f"{self.base_url}/instance-operations/launch"
        payload = {
            "region_name": region_name,
            "instance_type_name": instance_type_name,
            "ssh_key_names": ssh_key_names,
        }
        if name:
            payload["name"] = name
        if file_system_names:
            payload["file_system_names"] = file_system_names

        logger.info(f"Launching instance with payload: {payload}")

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def restart_instances(self, instance_ids: list[str]):
        """
        Restarts one or more instances.
        """
        url = f"{self.base_url}/instance-operations/restart"
        payload = {"instance_ids": instance_ids}

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def terminate_instances(self, instance_ids: list):
        """
        Terminates one or more instances.
        """
        url = f"{self.base_url}/instance-operations/terminate"
        payload = {"instance_ids": instance_ids}

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def list_instances(self):
        """
        Lists all running instances.
        """
        url = f"{self.base_url}/instances"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def get_instance_details(self, instance_id: str):
        """
        Retrieves details of a specific instance.
        """
        url = f"{self.base_url}/instances/{instance_id}"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def list_instance_types(self):
        """
        Lists all available instance types.
        """
        url = f"{self.base_url}/instance-types"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

class LambdaLabsAsyncClient(ProviderClient):
    def __init__(self, api_key: str = os.getenv("LAMBDA_API_KEY"), base_url: str = "https://cloud.lambdalabs.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def launch_instance(self, region_name: str, instance_type_name: str, ssh_key_names: list, name: str = None, file_system_names: list = None, user_data_script: str = None):
        """
        Launches a new instance asynchronously.
        """
        url = f"{self.base_url}/instance-operations/launch"
        payload = {
            "region_name": region_name,
            "instance_type_name": instance_type_name,
            "ssh_key_names": ssh_key_names,
            "user_data": user_data_script
        }
        if name:
            payload["name"] = name
        else:
            payload["name"] = "automated-deploy-test-3"
        if file_system_names:
            payload["file_system_names"] = file_system_names

        logger.info(f"Launching instance with payload: {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            # print response error
            if response.status_code < 200 or response.status_code >= 300:
                logger.error(f"Failed to launch instance: {response.status_code} - {response.text}")
            response.raise_for_status()
            return response.json()

    async def restart_instances(self, instance_ids: list[str]):
        """
        Restarts one or more instances asynchronously.
        """
        url = f"{self.base_url}/instance-operations/restart"
        payload = {"instance_ids": instance_ids}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def terminate_instances(self, instance_ids: list):
        """
        Terminates one or more instances asynchronously.
        """
        url = f"{self.base_url}/instance-operations/terminate"
        payload = {"instance_ids": instance_ids}

        logger.info(f"Terminating instance with payload: {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def list_instances(self):
        """
        Lists all running instances asynchronously.
        """
        url = f"{self.base_url}/instances"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            res = response.json()
            return res.get("data", [])

    async def get_instance_details(self, instance_id: str):
        """
        Retrieves details of a specific instance asynchronously.
        """
        url = f"{self.base_url}/instances/{instance_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def list_instance_types(self):
        """
        Lists all available instance types asynchronously.
        """
        url = f"{self.base_url}/instance-types"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
