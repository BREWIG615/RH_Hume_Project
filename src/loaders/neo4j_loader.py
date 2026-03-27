"""
Neo4j Loader

Batch loading utilities for Neo4j graph database.
"""

from typing import Generator, Optional
import logging
import pandas as pd
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """
    Neo4j batch loader for graph data.
    
    Example:
        loader = Neo4jLoader(uri="bolt://localhost:7687", user="neo4j", password="password")
        loader.load_nodes(df, label="Facility", id_field="id")
        loader.load_relationships(df, rel_type="STATIONED_AT", ...)
        loader.close()
    """
    
    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        batch_size: int = 1000
    ):
        """
        Initialize Neo4j loader.
        
        Args:
            uri: Neo4j bolt URI
            user: Username
            password: Password
            database: Database name
            batch_size: Records per transaction
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.batch_size = batch_size
        
        # Verify connectivity
        self.driver.verify_connectivity()
        logger.info(f"Connected to Neo4j: {uri}")
    
    def close(self):
        """Close the driver."""
        self.driver.close()
        logger.info("Neo4j connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _batches(self, df: pd.DataFrame) -> Generator[list[dict], None, None]:
        """Yield batches of records from DataFrame."""
        records = df.to_dict("records")
        for i in range(0, len(records), self.batch_size):
            yield records[i:i + self.batch_size]
    
    def execute_cypher(self, query: str, parameters: Optional[dict] = None) -> list[dict]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def load_nodes(
        self,
        df: pd.DataFrame,
        label: str,
        id_field: str,
        property_mapping: Optional[dict] = None
    ) -> int:
        """
        Load nodes from DataFrame.
        
        Args:
            df: DataFrame with node data
            label: Node label
            id_field: Field to use as node identifier
            property_mapping: Mapping of DataFrame columns to node properties
            
        Returns:
            Number of nodes created/updated
        """
        if property_mapping is None:
            property_mapping = {col: col for col in df.columns}
        
        # Build SET clause
        set_clauses = []
        for df_col, neo_prop in property_mapping.items():
            if df_col != id_field and df_col in df.columns:
                set_clauses.append(f"n.{neo_prop} = row.{df_col}")
        
        set_clause = ", ".join(set_clauses) if set_clauses else "n.id = row.id"
        
        query = f"""
        UNWIND $batch AS row
        MERGE (n:{label} {{{id_field}: row.{id_field}}})
        SET {set_clause}
        """
        
        total_loaded = 0
        with self.driver.session(database=self.database) as session:
            for batch in self._batches(df):
                result = session.run(query, batch=batch)
                summary = result.consume()
                total_loaded += summary.counters.nodes_created + summary.counters.properties_set
                logger.debug(f"Batch: created={summary.counters.nodes_created}, props={summary.counters.properties_set}")
        
        logger.info(f"Loaded {len(df)} {label} nodes")
        return total_loaded
    
    def load_relationships(
        self,
        df: pd.DataFrame,
        rel_type: str,
        source_label: str,
        source_id_field: str,
        target_label: str,
        target_id_field: str,
        source_df_field: str = "source_id",
        target_df_field: str = "target_id",
        property_mapping: Optional[dict] = None
    ) -> int:
        """
        Load relationships from DataFrame.
        
        Args:
            df: DataFrame with relationship data
            rel_type: Relationship type
            source_label: Source node label
            source_id_field: Source node ID field
            target_label: Target node label
            target_id_field: Target node ID field
            source_df_field: DataFrame column for source ID
            target_df_field: DataFrame column for target ID
            property_mapping: Mapping of DataFrame columns to relationship properties
            
        Returns:
            Number of relationships created
        """
        # Build SET clause for relationship properties
        if property_mapping:
            set_clauses = [f"r.{neo_prop} = row.{df_col}" for df_col, neo_prop in property_mapping.items()]
            set_clause = "SET " + ", ".join(set_clauses)
        else:
            set_clause = ""
        
        query = f"""
        UNWIND $batch AS row
        MATCH (source:{source_label} {{{source_id_field}: row.{source_df_field}}})
        MATCH (target:{target_label} {{{target_id_field}: row.{target_df_field}}})
        MERGE (source)-[r:{rel_type}]->(target)
        {set_clause}
        """
        
        total_loaded = 0
        with self.driver.session(database=self.database) as session:
            for batch in self._batches(df):
                result = session.run(query, batch=batch)
                summary = result.consume()
                total_loaded += summary.counters.relationships_created
                logger.debug(f"Batch: rels_created={summary.counters.relationships_created}")
        
        logger.info(f"Loaded {len(df)} {rel_type} relationships")
        return total_loaded
    
    def create_indexes(self, indexes: list[str]) -> int:
        """
        Create indexes.
        
        Args:
            indexes: List of CREATE INDEX statements
            
        Returns:
            Number of indexes created
        """
        created = 0
        with self.driver.session(database=self.database) as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.debug(f"Created index: {index_query[:50]}...")
                    created += 1
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.debug(f"Index already exists: {index_query[:50]}...")
                    else:
                        logger.error(f"Failed to create index: {e}")
        
        logger.info(f"Created {created} indexes")
        return created
    
    def clear_database(self, confirm: bool = False):
        """
        Clear all nodes and relationships.
        
        WARNING: This is destructive!
        
        Args:
            confirm: Must be True to execute
        """
        if not confirm:
            raise ValueError("Must set confirm=True to clear database")
        
        with self.driver.session(database=self.database) as session:
            # Delete in batches to avoid memory issues
            session.run("CALL apoc.periodic.iterate('MATCH (n) RETURN n', 'DETACH DELETE n', {batchSize:1000})")
        
        logger.warning("Database cleared!")
    
    def get_node_count(self, label: Optional[str] = None) -> int:
        """Get count of nodes with optional label filter."""
        if label:
            query = f"MATCH (n:{label}) RETURN count(n) as count"
        else:
            query = "MATCH (n) RETURN count(n) as count"
        
        result = self.execute_cypher(query)
        return result[0]["count"] if result else 0
    
    def get_relationship_count(self, rel_type: Optional[str] = None) -> int:
        """Get count of relationships with optional type filter."""
        if rel_type:
            query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
        else:
            query = "MATCH ()-[r]->() RETURN count(r) as count"
        
        result = self.execute_cypher(query)
        return result[0]["count"] if result else 0
