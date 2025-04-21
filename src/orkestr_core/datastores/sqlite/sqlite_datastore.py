import sqlite3
import json  # Add this import
from threading import Lock
from orkestr_core.base.datastore import Datastore
from orkestr_core.util.logger import setup_logger
from orkestr_core.base.datastore import GetAllNodesOutput, GetAllClustersOutput, GetAllServicesOutput
from orkestr_core.constants.providers import OrkestrRegion
from typing import Optional, Dict


logger = setup_logger(__name__)

class SQLiteDatastore(Datastore):
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = Lock()
        self._initialize_db()

    def _initialize_db(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    region TEXT,
                    data TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS node_specs (
                    node_spec_id TEXT PRIMARY KEY,
                    region TEXT,
                    data TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id TEXT PRIMARY KEY,
                    region TEXT,
                    data TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    service_id TEXT PRIMARY KEY,
                    data TEXT
                )
            """)
            conn.commit()

    def save_node(self, node):
        logger.info(f"Saving node {node.node_id} to SQLite datastore.")
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO nodes (node_id, region, data)
                VALUES (?, ?, ?)
            """, (node.node_id, node.region, json.dumps(node.model_dump()))) 
            conn.commit()

    def get_node(self, node_id, region: OrkestrRegion | str = None):
        logger.info(f"Getting node {node_id} from SQLite datastore.")
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT data FROM nodes WHERE node_id = ? AND region = ?
            """, (node_id, region_val))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None  # Return raw JSON
        
    def get_all_nodes(self, region: OrkestrRegion | str = None, limit=100, page=1, filters: Optional[Dict[str, str]] = None, **kwargs) -> GetAllNodesOutput:
        logger.info(f"Getting all nodes from SQLite datastore for region {region}.")
        offset = (page - 1) * limit
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        query = "SELECT data FROM nodes WHERE region = ?"
        params = [region_val]

        # Add filters to the query
        if filters:
            for key, value in filters.items():
                query += f" AND json_extract(data, '$.{key}') = ?"
                params.append(value)

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            nodes = [json.loads(row[0]) for row in rows]  # Deserialize JSON data

            # Get the total count of nodes for the region with filters applied
            count_query = "SELECT COUNT(*) FROM nodes WHERE region = ?"
            count_params = [region_val]

            if filters:
                for key, value in filters.items():
                    count_query += f" AND json_extract(data, '$.{key}') = ?"
                    count_params.append(value)

            cursor = conn.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]

        return GetAllNodesOutput(
            nodes=nodes,
            count=len(nodes),
            scanned_count=len(nodes),
            page=page,
            last_evaluated_key=None,  # Not applicable for SQLite
            has_more=(offset + len(nodes)) < total_count
        )

    def save_node_spec(self, node_spec):
        logger.info(f"Saving node spec {node_spec.id} to SQLite datastore.")
        try:
            with self.lock, sqlite3.connect(self.db_path, timeout=10) as conn:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO node_specs (node_spec_id, region, data)
                        VALUES (?, ?, ?)
                    """, (node_spec.id, node_spec.region, json.dumps(node_spec.model_dump()))) 
                    conn.commit()
                except Exception as e:
                    logger.error(f"1: Failed to save node spec Inside {node_spec.id}: {e}")
                    raise
        except Exception as e:
            logger.error(f"2: Failed to save node spec {node_spec.id}: {e}")
            raise

    def get_node_spec(self, node_spec_id, region: OrkestrRegion | str=None):
        logger.info(f"Getting node spec {node_spec_id} from SQLite datastore.")
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        with self.lock, sqlite3.connect(self.db_path, timeout=10) as conn:
            cursor = conn.execute("""
                SELECT data FROM node_specs WHERE node_spec_id = ? AND region = ?
            """, (node_spec_id, region_val))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None  # Return raw JSON

    def save_cluster(self, cluster):
        logger.info(f"Saving cluster {cluster.cluster_id} to SQLite datastore.")
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO clusters (cluster_id, region, data)
                VALUES (?, ?, ?)
            """, (cluster.cluster_id, cluster.region, json.dumps(cluster.model_dump()))) 
            conn.commit()

    def get_cluster(self, cluster_id: str, region: OrkestrRegion):
        logger.info(f"Getting cluster {cluster_id} from SQLite datastore.")
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT data FROM clusters WHERE cluster_id = ? AND region = ?
            """, (cluster_id, region_val))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None  # Return raw JSON
        
    def get_all_clusters(self, region: OrkestrRegion | str, limit=100, page=1, **kwargs) -> GetAllClustersOutput:
        region_val = region.value if isinstance(region, OrkestrRegion) else region
        logger.info(f"Getting all clusters from SQLite datastore for region {region_val}.")
        offset = (page - 1)  * limit
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT data FROM clusters WHERE region = ? LIMIT ? OFFSET ?
            """, (region_val, limit, offset))
            rows = cursor.fetchall()
            clusters = [json.loads(row[0]) for row in rows]
            # Get the total count of clusters for the region
            cursor = conn.execute("""
                SELECT COUNT(*) FROM clusters WHERE region = ?
            """, (region_val,))
            total_count = cursor.fetchone()[0]
        return GetAllClustersOutput(
            clusters=clusters,
            count=len(clusters),
            scanned_count=len(clusters),
            page=page,
            last_evaluated_key=None,  # Not applicable for SQLite
            has_more=(offset + len(clusters)) < total_count
        )

    def save_service(self, service):
        logger.info(f"Saving service {service.service_id} to SQLite datastore.")
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO services (service_id, data)
                VALUES (?, ?)
            """, (service.service_id, json.dumps(service.model_dump())))
            conn.commit()

    def get_service(self, service_id):
        logger.info(f"Getting service {service_id} from SQLite datastore.")
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT data FROM services WHERE service_id = ?
            """, (service_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None  # Return raw JSON

    def get_all_services(self, limit=100, page=1, **kwargs) -> GetAllServicesOutput:
        logger.info(f"Getting all services from SQLite datastore.")
        offset = (page - 1)  * limit
        with self.lock, sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT data FROM services LIMIT ? OFFSET ? 
            """, (limit, offset))
            rows = cursor.fetchall()
            services = [json.loads(row[0]) for row in rows]
            # Get the total count of services
            cursor = conn.execute("""
                SELECT COUNT(*) FROM services 
            """)
            total_count = cursor.fetchone()[0]
        return GetAllServicesOutput(
            services=services,
            count=len(services),
            scanned_count=len(services),
            page=page,
            last_evaluated_key=None,  # Not applicable for SQLite
            has_more=(offset + len(services)) < total_count
        )