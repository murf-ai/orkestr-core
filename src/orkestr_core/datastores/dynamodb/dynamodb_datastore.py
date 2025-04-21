from orkestr_core.base.datastore import Datastore
from orkestr_core.constants.providers import OrkestrRegion
from typing import Optional, Dict
from boto3.dynamodb.conditions import Key, Attr
import json
from orkestr_core.base.datastore import GetAllNodesOutput, GetAllClustersOutput, GetAllServicesOutput

class DynamoDBDatastore(Datastore):
    def __init__(self, table):
        self.table = table

    def save_node(self, node):
        self.table.put_item(Item={"partitionKey": f"NODE#{node.region}", "sortKey": node.node_id, "Data": node.model_dump()})

    def get_node(self, node_id, region: OrkestrRegion | str):
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        response = self.table.get_item(Key={"partitionKey": f"NODE#{region_val}", "sortKey": node_id})
        node_data = response.get("Item", {}).get("Data")
        return node_data
    
    def get_all_nodes(self, region: OrkestrRegion | str, limit=100, page=1, last_node=None, filters: Optional[Dict[str, str]] = None) -> GetAllNodesOutput:
        nodes = []
        filter_expression = None
        region_val = region.value if isinstance(region, OrkestrRegion) else region

        if filters:
            filter_conditions = []
            for key, value in filters.items():
                filter_conditions.append(Attr(key).eq(value))
            if filter_conditions:
                filter_expression = filter_conditions[0]
                for condition in filter_conditions[1:]:
                    filter_expression &= condition

        query_params = {
            "KeyConditionExpression": Key("partitionKey").eq(f"NODE#{region_val}"),
            "Limit": limit,
        }
        if filter_expression:
            query_params["FilterExpression"] = filter_expression
        if last_node:
            query_params["ExclusiveStartKey"] = last_node

        response = self.table.query(
            **query_params
        )
        items = response.get("Items", [])
        for item in items:
            node_data = item.get("Data")
            if node_data:
                nodes.append(node_data)
        count = response.get('Count', 0)
        scanned_count = response.get('ScannedCount', 0)
        last_evaluated_key = response.get('LastEvaluatedKey', None)
        return GetAllNodesOutput(
            nodes=nodes,
            count=count,
            scanned_count=scanned_count,
            page=page,
            last_evaluated_key=last_evaluated_key,
            has_more=last_evaluated_key is not None
        )

    def save_node_spec(self, node_spec):
        self.table.put_item(Item={"partitionKey": f"NODE_SPEC#{node_spec.region}", "sortKey": node_spec.id, "Data": node_spec.model_dump()})

    def get_node_spec(self, node_spec_id, region: OrkestrRegion | str):
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        response = self.table.get_item(Key={"partitionKey": f"NODE_SPEC#{region_val}", "sortKey": node_spec_id})
        return response.get("Item", {}).get("Data")

    def save_cluster(self, cluster):
        self.table.put_item(Item={"partitionKey": f"CLUSTER#{cluster.region}", "sortKey": cluster.cluster_id, "Data": cluster.model_dump()})

    def get_cluster(self, cluster_id, region: OrkestrRegion | str):
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        response = self.table.get_item(Key={"partitionKey": f"CLUSTER#{region_val}", "sortKey": cluster_id})
        return response.get("Item", {}).get("Data")
    
    def get_all_clusters(self, region: OrkestrRegion | str, limit=100, page=1, last_cluster=None) -> GetAllClustersOutput:
        clusters = []
        region_val = region.value if isinstance(region, OrkestrRegion) else region

        query_params = {
            "KeyConditionExpression": Key("partitionKey").eq(f"CLUSTER#{region_val}"),
            "Limit": limit,
        }
        if last_cluster:
            query_params["ExclusiveStartKey"] = last_cluster

        response = self.table.query(
            **query_params
        )
        items = response.get("Items", [])
        for item in items:
            cluster_data = item.get("Data")
            if cluster_data:
                clusters.append(cluster_data)
        count = response.get('Count', 0)
        scanned_count = response.get('ScannedCount', 0)
        last_evaluated_key = response.get('LastEvaluatedKey', None)
        return GetAllClustersOutput(
            clusters=clusters,
            count=count,
            scanned_count=scanned_count,
            page=page,
            last_evaluated_key=last_evaluated_key,
            has_more=last_evaluated_key is not None
        )

    def save_service(self, service):
        self.table.put_item(Item={"partitionKey": "SERVICE", "sortKey": service.service_id, "Data": service.model_dump()})

    def get_service(self, service_id):
        response = self.table.get_item(Key={"partitionKey": "SERVICE", "sortKey": service_id})
        return response.get("Item", {}).get("Data")
    
    def get_all_services(self, limit=100, page=1, last_service=None) -> GetAllServicesOutput:
        services = []
        query_params = {
            "KeyConditionExpression": Key("partitionKey").eq("SERVICE"),
            "Limit": limit,
        }
        if last_service:
            query_params["ExclusiveStartKey"] = last_service

        response = self.table.query(
            **query_params
        )
        items = response.get("Items", [])
        for item in items:
            service_data = item.get("Data")
            if service_data:
                services.append(service_data)
        count = response.get('Count', 0)
        scanned_count = response.get('ScannedCount', 0)
        last_evaluated_key = response.get('LastEvaluatedKey', None)
        return GetAllServicesOutput(
            services=services,
            count=count,
            scanned_count=scanned_count,
            page=page,
            last_evaluated_key=last_evaluated_key,
            has_more=last_evaluated_key is not None
        )
