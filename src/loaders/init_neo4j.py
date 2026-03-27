"""
Neo4j Initialization

Creates indexes and constraints for the graph schema.
"""

import logging
from src.config.loader import get_neo4j_config
from src.loaders.neo4j_loader import Neo4jLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Index definitions
INDEXES = [
    # Node indexes
    "CREATE INDEX IF NOT EXISTS FOR (f:Facility) ON (f.id)",
    "CREATE INDEX IF NOT EXISTS FOR (f:Facility) ON (f.name)",
    "CREATE INDEX IF NOT EXISTS FOR (a:Asset) ON (a.id)",
    "CREATE INDEX IF NOT EXISTS FOR (a:Asset) ON (a.status)",
    "CREATE INDEX IF NOT EXISTS FOR (r:Route) ON (r.id)",
    "CREATE INDEX IF NOT EXISTS FOR (r:Route) ON (r.access_status)",
    "CREATE INDEX IF NOT EXISTS FOR (w:Waypoint) ON (w.id)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Chokepoint) ON (c.id)",
    "CREATE INDEX IF NOT EXISTS FOR (p:Part) ON (p.id)",
    "CREATE INDEX IF NOT EXISTS FOR (m:Manifest) ON (m.id)",
    "CREATE INDEX IF NOT EXISTS FOR (wo:WorkOrder) ON (wo.id)",
    "CREATE INDEX IF NOT EXISTS FOR (wo:WorkOrder) ON (wo.status)",
    "CREATE INDEX IF NOT EXISTS FOR (i:Inventory) ON (i.id)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Communication) ON (c.id)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Communication) ON (c.hume_status)",
    "CREATE INDEX IF NOT EXISTS FOR (d:Disruption) ON (d.id)",
    "CREATE INDEX IF NOT EXISTS FOR (d:Disruption) ON (d.status)",
    "CREATE INDEX IF NOT EXISTS FOR (s:Source) ON (s.id)",
    "CREATE INDEX IF NOT EXISTS FOR (rg:Region) ON (rg.id)",
    "CREATE INDEX IF NOT EXISTS FOR (ri:ReviewItem) ON (ri.id)",
    "CREATE INDEX IF NOT EXISTS FOR (ri:ReviewItem) ON (ri.status)",
    "CREATE INDEX IF NOT EXISTS FOR (ri:ReviewItem) ON (ri.priority)",
    "CREATE INDEX IF NOT EXISTS FOR (sc:StateChange) ON (sc.id)",
    
    # Composite indexes for common queries
    "CREATE INDEX IF NOT EXISTS FOR (a:Asset) ON (a.facility_id, a.status)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Communication) ON (c.facility_id, c.hume_status)",
]

# Constraint definitions (optional, for data integrity)
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Facility) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Route) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (w:Waypoint) REQUIRE w.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Part) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Communication) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (ri:ReviewItem) REQUIRE ri.id IS UNIQUE",
]


def init_neo4j(loader: Neo4jLoader = None) -> bool:
    """
    Initialize Neo4j schema (indexes and constraints).
    
    Args:
        loader: Neo4j loader instance (creates one if not provided)
        
    Returns:
        True if successful
    """
    close_loader = False
    if loader is None:
        config = get_neo4j_config()
        loader = Neo4jLoader(
            uri=config["uri"],
            user=config["user"],
            password=config["password"],
            database=config.get("database", "neo4j")
        )
        close_loader = True
    
    try:
        logger.info("Creating indexes...")
        for index in INDEXES:
            try:
                loader.execute_cypher(index)
                logger.debug(f"Created: {index[:60]}...")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Index creation failed: {e}")
        
        logger.info("Creating constraints...")
        for constraint in CONSTRAINTS:
            try:
                loader.execute_cypher(constraint)
                logger.debug(f"Created: {constraint[:60]}...")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Constraint creation failed: {e}")
        
        logger.info("Neo4j initialization complete")
        return True
        
    finally:
        if close_loader:
            loader.close()


def verify_schema(loader: Neo4jLoader = None) -> dict:
    """
    Verify schema is properly initialized.
    
    Args:
        loader: Neo4j loader instance
        
    Returns:
        Dictionary with schema information
    """
    close_loader = False
    if loader is None:
        config = get_neo4j_config()
        loader = Neo4jLoader(
            uri=config["uri"],
            user=config["user"],
            password=config["password"]
        )
        close_loader = True
    
    try:
        # Get index count
        indexes = loader.execute_cypher("SHOW INDEXES YIELD name RETURN count(name) as count")
        index_count = indexes[0]["count"] if indexes else 0
        
        # Get constraint count
        constraints = loader.execute_cypher("SHOW CONSTRAINTS YIELD name RETURN count(name) as count")
        constraint_count = constraints[0]["count"] if constraints else 0
        
        # Get node labels
        labels = loader.execute_cypher("CALL db.labels() YIELD label RETURN collect(label) as labels")
        label_list = labels[0]["labels"] if labels else []
        
        # Get relationship types
        rel_types = loader.execute_cypher("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types")
        rel_type_list = rel_types[0]["types"] if rel_types else []
        
        return {
            "indexes": index_count,
            "constraints": constraint_count,
            "labels": label_list,
            "relationship_types": rel_type_list,
        }
        
    finally:
        if close_loader:
            loader.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        info = verify_schema()
        print("Neo4j Schema Status:")
        print(f"  Indexes: {info['indexes']}")
        print(f"  Constraints: {info['constraints']}")
        print(f"  Labels: {info['labels']}")
        print(f"  Relationship Types: {info['relationship_types']}")
    else:
        success = init_neo4j()
        sys.exit(0 if success else 1)
