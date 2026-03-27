"""ETL Pipeline - Transform raw data to processed."""
import logging
from pathlib import Path
import pandas as pd
from src.config.loader import get_data_paths

logger = logging.getLogger(__name__)

def run_etl():
    """Run ETL transformations."""
    paths = get_data_paths()
    raw_dir = Path(paths.get("synthetic", "data/synthetic"))
    processed_dir = Path(paths.get("processed", "data/processed"))
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy and transform each entity type
    for entity in ["facilities", "assets", "routes", "communications", "chokepoints"]:
        src = raw_dir / f"{entity}.parquet"
        if src.exists():
            df = pd.read_parquet(src)
            # Add processing timestamp
            df["_processed_at"] = pd.Timestamp.now().isoformat()
            df.to_parquet(processed_dir / f"{entity}.parquet", index=False)
            logger.info(f"Processed {entity}: {len(df)} records")
    
    logger.info("ETL complete")
