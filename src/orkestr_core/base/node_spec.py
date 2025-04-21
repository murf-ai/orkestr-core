from pydantic import BaseModel, Field
from typing import Dict, List
import uuid

class NodeSpecConfiguration(BaseModel):
    machine_type: str
    user_data_script: str
    environment_variables: Dict[str, str]

class NodeSpec(BaseModel):
    """
    Represents a specification for a cluster's nodes with configurable properties.

    Attributes:
        id (str): Unique identifier for the spec.
        name (str): Name of the spec.
        versions (List[NodeSpecConfiguration]): List of configurations for the spec.
        default_version (int): Index of the default version to use.
        region (str): The region where the spec is applicable.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))
    versions: List[NodeSpecConfiguration]
    default_version: int = 0
    region: str

    def get_version(self, version: int) -> NodeSpecConfiguration:
        try:
            return self.versions[version]
        except IndexError:
            raise ValueError(f"Version {version} not found for NodeSpec {self.id}.")
    
    def get_latest_version(self) -> NodeSpecConfiguration:
        return self.versions[-1]

    def get_default_version(self) -> NodeSpecConfiguration:
        return self.versions[self.default_version]
    
    def set_default_version(self, version: int) -> None:
        if version < 0 or version >= len(self.versions):
            raise ValueError(f"Invalid version {version} for NodeSpec {self.id}.")
        self.default_version = version
    
    def create_new_version(self, machine_type: str, user_data_script: str, environment_variables: Dict[str, str], set_default: bool = False) -> None:
        new_version = NodeSpecConfiguration(
            machine_type=machine_type,
            user_data_script=user_data_script,
            environment_variables=environment_variables
        )
        self.versions.append(new_version)
        if set_default:
            self.set_default_version(len(self.versions) - 1)
        # return the version number
        return len(self.versions) - 1
    

