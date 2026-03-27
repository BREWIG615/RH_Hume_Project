"""Qlik Presentation Layer - Generate denormalized tables for Qlik."""
import logging
from pathlib import Path
import pandas as pd
from src.config.loader import get_data_paths

logger = logging.getLogger(__name__)

def generate_presentation_layer():
    """Generate Qlik-optimized presentation tables."""
    paths = get_data_paths()
    processed_dir = Path(paths.get("processed", "data/processed"))
    presentation_dir = Path(paths.get("presentation", "data/presentation"))
    presentation_dir.mkdir(parents=True, exist_ok=True)
    
    # Facility summary with asset counts
    facilities = pd.read_parquet(processed_dir / "facilities.parquet")
    assets = pd.read_parquet(processed_dir / "assets.parquet")
    
    asset_summary = assets.groupby("facility_id").agg({
        "id": "count",
        "status": lambda x: (x == "FMC").sum()
    }).rename(columns={"id": "total_assets", "status": "fmc_count"})
    
    facility_summary = facilities.merge(asset_summary, left_on="id", right_index=True, how="left")
    facility_summary.to_parquet(presentation_dir / "facility_summary.parquet", index=False)
    
    logger.info("Presentation layer generated")
