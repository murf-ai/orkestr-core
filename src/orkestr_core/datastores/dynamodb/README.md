## DynamoDB Datastore

Orkestr provides a DynamoDB-based implementation of the `Datastore` interface. This implementation uses a boto3 DynamoDB table resource to store and retrieve data. Each entity (e.g., Node, Cluster, Service) is stored with a composite key consisting of:

- **partitionKey**: Partition Key, which is:
  - For `Node`, `NodeSpec` and `Cluster`, a combination of the entity type and the region (e.g., `NODE#us-west-2`, `CLUSTER#us-west-2`).
  - For `Service`, just the entity type (e.g., `SERVICE`).
- **sortKey**: Sort Key, which is the unique identifier for the entity (e.g., `node_id`, `cluster_id`, `service_id`).

### Example Usage

```python
import boto3
from orkestr_core.datastores.dynamodb.datastore import DynamoDBDatastore

# Initialize the DynamoDB table resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("YourTableName")

# Create the DynamoDB datastore
datastore = DynamoDBDatastore(table)

# Example: Save and retrieve a node
node = Node(node_id="node1", region="us-west-2", ...)  # Replace with actual Node initialization
datastore.save_node(node)
retrieved_node = datastore.get_node(node_id="node1", region="us-west-2")

# Example: Save and retrieve a cluster
cluster = Cluster(cluster_id="cluster1", region="us-west-2", ...)  # Replace with actual Cluster initialization
datastore.save_cluster(cluster)
retrieved_cluster = datastore.get_cluster(cluster_id="cluster1", region="us-west-2")

# Example: Save and retrieve a service
service = Service(service_id="service1", ...)  # Replace with actual Service initialization
datastore.save_service(service)
retrieved_service = datastore.get_service(service_id="service1")
```

## Important Notes

- Ensure that the DynamoDB table is created with the appropriate partition and sort key schema.
- Ensure that the AWS credentials and region are configured correctly in your environment.
