"""Hume Processor - Batch process communications through Hume AI."""
import logging
from pathlib import Path
import pandas as pd
from src.config.loader import get_data_paths, get_hume_config
from src.integrations.hume_client import HumeClient

logger = logging.getLogger(__name__)

def process_batch():
    """Process pending communications through Hume."""
    paths = get_data_paths()
    processed_dir = Path(paths.get("processed", "data/processed"))
    
    df = pd.read_parquet(processed_dir / "communications.parquet")
    pending = df[df["hume_status"] == "pending"]
    
    logger.info(f"Processing {len(pending)} communications through Hume")
    
    client = HumeClient()
    results = []
    
    for _, row in pending.iterrows():
        scores = client.analyze_text(row["content"])
        results.append({
            "id": row["id"],
            "hume_anxiety": scores.get("anxiety", 0),
            "hume_urgency": scores.get("urgency", 0),
            "hume_confusion": scores.get("confusion", 0),
            "hume_fear": scores.get("fear", 0),
            "hume_status": "processed",
        })
    
    # Merge results back
    results_df = pd.DataFrame(results)
    df = df.merge(results_df, on="id", how="left", suffixes=("", "_new"))
    
    # Update columns
    for col in ["hume_anxiety", "hume_urgency", "hume_confusion", "hume_fear", "hume_status"]:
        if f"{col}_new" in df.columns:
            df[col] = df[f"{col}_new"].fillna(df[col])
            df.drop(f"{col}_new", axis=1, inplace=True)
    
    df.to_parquet(processed_dir / "communications.parquet", index=False)
    logger.info(f"Hume processing complete: {len(results)} processed")
