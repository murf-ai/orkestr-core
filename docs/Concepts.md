## Concepts

Orkestr is built around the following concepts:

- **Node**: A node is a single instance of a virtual machine, container, or any other type of compute resource. A node can be a physical machine, a virtual machine, a container, or any other type of compute resource.
- **Cluster**: A cluster is a group of nodes that are managed as a single unit. A cluster can be a group of virtual machines, containers, or any other type of node.
- **Service**: A service is a group of clusters that are managed as a single unit.
- **Provider**: A provider is a cloud provider that provides compute resources.
- **Datastore**: A datastore is a storage system that is used to store the state of the infrastructure and services.
- **Event Bus**: An event bus is a message broker that is used to send and receive events between different components of the system.
- **Scheduler**: A scheduler is a component that is used to schedule tasks and events in the system.
- **Orchestrator**: An orchestrator is responsible for managing the lifecycle of clusters and nodes, ensuring that the desired state of the infrastructure is maintained.

### Cluster

Use a cluster when you need to manage a group of nodes that will have the same set of configurations. A cluster will comprise of a single instance/machine type and the infra will be deployed to a single region. You can define the configurations like machine type, user data script, environment variables, etc. to deploy multiple nodes together in a cluster. You can set up the minimum, maximum, and desired number of nodes in a cluster.

When a machine in a cluster goes down, Orkestr will automatically replace it with a new machine. You can also manually scale the cluster by setting the desired number of nodes in a cluster.

### Service

> @todo: This feature is not yet implemented.

Use a service when you need to manage a group of clusters. The clusters are expected (but not required) to run the same application/task. Services help you do things like

- blue/green deployments
  - You can define a set of clusters as the blue cluster and another set of clusters as the green cluster.
- Autoscaling
  - By default, the service will distribute the scale evenly across the clusters while respecting the min/max values. You can also set the weight of each cluster to distribute the scale based on the weight.
  - Clusters are scaled by setting the desired number of nodes in a cluster.
- High availability by deploying clusters in multiple regions
  - You can create multiple clusters in different regions and add them to a service.
  - Set the weights of each cluster to give preference to a specific instance type or region.

### Provider

Orkestr is designed to be provider-agnostic. You can use any cloud provider that provides compute resources. You can also use multiple providers in a single Orkestr instance. Each provider will have to configure their implementations of `Node`. Each provider is also expected to have a `client` that will interact with the provider's API.

Orkestr provides implementations of the `Provider` interface for the following cloud providers:

- [Lambda Labs](./src/orkestr_core/providers/lambda_labs/README.md)

### Datastore

Orkestr uses a datastore to store the state of the infrastructure and services. You can use any datastore implementation available in Orkestr or create your own implementation by extending the `Datastore` interface. The datastore is used to store the state of the nodes, clusters, and services.

Orkestr provides implementations of the `Datastore` interface for the following storage systems:

- [DynamoDB](./src/orkestr_core/datastores/dynamodb/README.md)
- [SQLite](./src/orkestr_core/datastores/sqlite/README.md)

## Drift Detector

The Drift Detector is a critical component of Orkestr that ensures the desired state of infrastructure and services is maintained.

For more details, see the [Drift Detector documentation](./src/orkestr_core/base/drift_detector/README.md).

## Event Bus

The Event Bus is a message broker that is used to send and receive events between different components of the system. It is used to decouple the components of the system and allow them to communicate with each other asynchronously.

## Scheduler

The Scheduler can asynchronously run tasks at a specific interval or at a specific time.

## Monitoring

Health checks are implemented by combining the drift detector, event bus, and scheduler. The scheduler will run the drift detector at a specific interval. The drift detector will check the state of the infrastructure and services and send events to the event bus if there are any discrepancies. The event bus will then notify the appropriate components to take action.

### Orchestrator

The orchestrator is a core component of Orkestr that manages the lifecycle of clusters and nodes. It ensures that the desired state of the infrastructure is maintained by handling tasks such as scaling, adding, or removing nodes, and resolving drift.

The orchestrator interacts with the event bus to listen for events and take appropriate actions. It also communicates with the datastore to retrieve and update the state of clusters and nodes.
