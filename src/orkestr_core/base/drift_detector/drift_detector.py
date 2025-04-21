from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

def detect_node_drift(orkestr_node_data: dict, provider_node_data: dict) -> bool:
        """
        Detects drift between the desired and actual state.
        Returns True if drift is detected, False otherwise.
        """
        status = orkestr_node_data.status
        provider_status = provider_node_data.get("status")
        node_id = orkestr_node_data.node_id
        cluster_id = orkestr_node_data.cluster_id
        provider = orkestr_node_data.provider
        if status and status != provider_status:
            logger.warning(f"Drift detected for Node {node_id} in cluster {cluster_id} - {provider}. Expected status: {status}, Actual status: {provider_status}.")
            return True
        return False