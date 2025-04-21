## Introduction

Orkestr is a framework for orchestrating infrastructure and services in a multi-cloud environment. It is designed to be a lightweight, flexible, and extensible framework that can be used to manage infrastructure and services.

> **Note**: Orkestr is currently in the early stages of development. The API and functionality may change as we continue to develop the framework.

## Installation

To install Orkestr, you can use pip:

```bash
pip install orkestr-core
```

## Usage

Here is an example of how to initialize an Orkestr instance, create a cluster, and scale it:

```python
import asyncio
from orkestr_core import Orkestr, Cluster, Service
from orkestr_core.constants.providers import ProviderName, OrkestrRegion
from orkestr_core.base.node_spec import NodeSpec, NodeSpecConfiguration
from orkestr_core.base.service import ClusterConfiguration
from orkestr_core.datastores.global_datastore import set_global_datastore
from orkestr_core.datastores.sqlite.sqlite_datastore import SQLiteDatastore

async def main():
    # Set up the datastore
    datastore = SQLiteDatastore(db_path='orkestr.db')
    set_global_datastore(datastore)

    # Initialize Orkestr
    orkestr = Orkestr(
        providers=[ProviderName.TEST_PROVIDER],
        regions=[OrkestrRegion.US_EAST_1]
    )
    await orkestr.start_scheduler()

    # Define a NodeSpec
    node_spec_config = NodeSpecConfiguration(
        machine_type="t2.micro",
        user_data_script="echo 'Hello World'",
        environment_variables={}
    )
    node_spec = NodeSpec(
        name="ExampleNodeSpec",
        region=OrkestrRegion.US_EAST_1,
        versions=[node_spec_config]
    )

    # Define a Cluster
    cluster = Cluster(
        name="ExampleCluster",
        cluster_id="example_cluster",
        region=OrkestrRegion.US_EAST_1,
        provider=ProviderName.TEST_PROVIDER,
        node_spec_id=node_spec.id,
        node_spec_version=0,
        max_nodes=3
    )

    # Save configurations to the datastore
    datastore.save_node_spec(node_spec)
    datastore.save_cluster(cluster)

    # Scale the cluster
    orkestr.cluster_orchestrator.scale(
        cluster_id=cluster.cluster_id,
        region=OrkestrRegion.US_EAST_1,
        desired_nodes=2
    )

    print("Cluster scaled successfully!")

# Run the example
asyncio.run(main())
```

## Docs

To know more about Orkestr, see the [Docs](./docs/README.md).
