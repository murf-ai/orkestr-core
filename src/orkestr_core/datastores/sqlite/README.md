## SQLite Datastore

Orkestr provides an SQLite-based implementation of the `Datastore` interface. This implementation uses SQLite as a lightweight, file-based database to store and retrieve data. Each entity (e.g., Node, Cluster, Service) is stored in a dedicated table.

> **Note**: Not recommended for production use. Use DynamoDB or another robust database for production environments.

### Tables

The following tables are created in the SQLite database:

- **nodes**: Stores node data with columns:

  - `node_id`: Primary key for the node.
  - `region`: The region associated with the node.
  - `data`: JSON-encoded data for the node.

- **node_specs**: Stores node specification data with columns:

  - `node_spec_id`: Primary key for the node specification.
  - `region`: The region associated with the node specification.
  - `data`: JSON-encoded data for the node specification.

- **clusters**: Stores cluster data with columns:

  - `cluster_id`: Primary key for the cluster.
  - `region`: The region associated with the cluster.
  - `data`: JSON-encoded data for the cluster.

- **services**: Stores service data with columns:
  - `service_id`: Primary key for the service.
  - `data`: JSON-encoded data for the service.

### Example Usage

```python
from orkestr_core.datastores.sqlite.sqlite_datastore import SQLiteDatastore

# Initialize the SQLite datastore
datastore = SQLiteDatastore(db_path="path/to/your/database.db")

# Example: Save and retrieve a node
node = Node(node_id="node1", region="us-west-2", ...)
datastore.save_node(node)
retrieved_node = datastore.get_node(node_id="node1", region="us-west-2")

# Example: Save and retrieve a cluster
cluster = Cluster(cluster_id="cluster1", region="us-west-2", ...)
datastore.save_cluster(cluster)
retrieved_cluster = datastore.get_cluster(cluster_id="cluster1", region="us-west-2")

# Example: Save and retrieve a service
service = Service(service_id="service1", ...)
datastore.save_service(service)
retrieved_service = datastore.get_service(service_id="service1")
```

### Important Notes

- Ensure that the SQLite database file is accessible and writable by the application.
- SQLite is suitable for lightweight, single-user, or low-concurrency use cases. For high-concurrency or distributed systems, consider using a more robust database like DynamoDB.
- The `SQLiteDatastore` implementation uses a threading lock to ensure thread safety during database operations.
