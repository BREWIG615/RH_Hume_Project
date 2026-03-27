"""Neo4j Loader Job - Load processed data into Neo4j."""
import logging
from pathlib import Path
import pandas as pd
from src.config.loader import get_data_paths, get_neo4j_config
from src.loaders.neo4j_loader import Neo4jLoader

logger = logging.getLogger(__name__)

def load_all():
    """Load all entities into Neo4j."""
    paths = get_data_paths()
    processed_dir = Path(paths.get("processed", "data/processed"))
    
    config = get_neo4j_config()
    loader = Neo4jLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"]
    )
    
    try:
        # Load facilities
        df = pd.read_parquet(processed_dir / "facilities.parquet")
        loader.load_nodes(df, "Facility", "id")
        
        # Load assets
        df = pd.read_parquet(processed_dir / "assets.parquet")
        loader.load_nodes(df, "Asset", "id")
        
        # Load routes
        df = pd.read_parquet(processed_dir / "routes.parquet")
        loader.load_nodes(df, "Route", "id")
        
        # Load communications
        df = pd.read_parquet(processed_dir / "communications.parquet")
        loader.load_nodes(df, "Communication", "id")
        
        # Load chokepoints
        df = pd.read_parquet(processed_dir / "chokepoints.parquet")
        loader.load_nodes(df, "Chokepoint", "id")
        
        logger.info("Neo4j load complete")
    finally:
        loader.close()
