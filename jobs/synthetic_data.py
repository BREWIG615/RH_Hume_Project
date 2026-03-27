"""
Synthetic Data Generator

Generates realistic demo data for the contested logistics platform.
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pandas as pd

from src.config.loader import get_config, get_data_paths

logger = logging.getLogger(__name__)

# Indo-Pacific facilities
FACILITIES = [
    {"id": "yokosuka", "name": "Yokosuka Naval Base", "type": "port", "lat": 35.2833, "lon": 139.6667, "region": "japan"},
    {"id": "kadena", "name": "Kadena Air Base", "type": "airfield", "lat": 26.3516, "lon": 127.7692, "region": "okinawa"},
    {"id": "sasebo", "name": "Sasebo Naval Base", "type": "port", "lat": 33.1592, "lon": 129.7228, "region": "japan"},
    {"id": "yokota", "name": "Yokota Air Base", "type": "airfield", "lat": 35.7485, "lon": 139.3487, "region": "japan"},
    {"id": "camp_fuji", "name": "Camp Fuji", "type": "depot", "lat": 35.3019, "lon": 138.7644, "region": "japan"},
    {"id": "guam", "name": "Naval Base Guam", "type": "port", "lat": 13.4443, "lon": 144.7937, "region": "guam"},
    {"id": "pearl_harbor", "name": "Pearl Harbor", "type": "port", "lat": 21.3545, "lon": -157.9500, "region": "hawaii"},
    {"id": "singapore", "name": "Changi Naval Base", "type": "port", "lat": 1.3521, "lon": 103.9896, "region": "singapore"},
    {"id": "diego_garcia", "name": "Diego Garcia", "type": "airfield", "lat": -7.3133, "lon": 72.4111, "region": "indian_ocean"},
    {"id": "subic", "name": "Subic Bay", "type": "port", "lat": 14.7944, "lon": 120.2833, "region": "philippines"},
]

# Strategic chokepoints
CHOKEPOINTS = [
    {"id": "taiwan_strait", "name": "Taiwan Strait", "lat": 24.5, "lon": 119.5, "importance": "critical"},
    {"id": "luzon_strait", "name": "Luzon Strait", "lat": 20.5, "lon": 121.5, "importance": "high"},
    {"id": "malacca_strait", "name": "Malacca Strait", "lat": 2.5, "lon": 101.5, "importance": "critical"},
    {"id": "miyako_strait", "name": "Miyako Strait", "lat": 24.8, "lon": 125.3, "importance": "high"},
    {"id": "korea_strait", "name": "Korea Strait", "lat": 34.0, "lon": 129.5, "importance": "medium"},
]

# Communication templates for different emotional states
COMM_TEMPLATES = {
    "normal": [
        "Routine status update: all systems nominal. Proceeding as scheduled.",
        "Inventory count complete. Stock levels within acceptable ranges.",
        "Morning briefing concluded. No significant issues to report.",
        "Equipment maintenance completed successfully. Ready for operations.",
    ],
    "anxious": [
        "Concerned about the recent increase in activity near the strait. Monitoring closely.",
        "Worried about supply chain delays affecting our readiness. Need guidance.",
        "Uncertain about the new routing protocols. Request clarification.",
        "Feeling uneasy about the timeline. We may not meet the deadline.",
    ],
    "urgent": [
        "URGENT: Immediate assistance required. Critical shortage developing.",
        "Priority message: Need authorization ASAP for emergency procurement.",
        "Time-sensitive: Route assessment needed before 0600 tomorrow.",
        "Critical: Equipment failure affecting mission capability. Need parts immediately.",
    ],
    "fearful": [
        "Alert: Potential threat detected in sector. Recommend heightened awareness.",
        "Serious concerns about personnel safety given current situation.",
        "Request immediate guidance on evacuation protocols.",
        "Growing threat indicators require immediate attention.",
    ],
}


def generate_facilities(config: dict) -> pd.DataFrame:
    """Generate facility data."""
    count = config.get("counts", {}).get("facilities", len(FACILITIES))
    facilities = FACILITIES[:count]
    
    records = []
    for f in facilities:
        records.append({
            "id": f["id"],
            "name": f["name"],
            "facility_type": f["type"],
            "latitude": f["lat"],
            "longitude": f["lon"],
            "region_id": f["region"],
            "operational_status": "operational",
            "capabilities": ["storage", "maintenance", "refuel"],
            "_source_system": "synthetic",
            "_confidence": 1.0,
            "_classification": "UNCLASSIFIED",
        })
    
    return pd.DataFrame(records)


def generate_assets(config: dict, facilities: pd.DataFrame) -> pd.DataFrame:
    """Generate asset data."""
    count = config.get("counts", {}).get("assets", 100)
    scenario = config.get("scenario", "baseline")
    
    asset_types = ["truck", "aircraft", "vessel", "container", "equipment"]
    statuses = ["FMC", "PMCM", "PMCS", "NMCM", "NMCS"]
    
    # Adjust status distribution based on scenario
    if scenario == "disrupted":
        status_weights = [0.6, 0.15, 0.1, 0.1, 0.05]  # Lower FMC
    else:
        status_weights = [0.8, 0.1, 0.05, 0.03, 0.02]  # Higher FMC
    
    records = []
    facility_ids = facilities["id"].tolist()
    
    for i in range(count):
        asset_type = random.choice(asset_types)
        records.append({
            "id": f"asset_{i:04d}",
            "name": f"{asset_type.title()} {i:04d}",
            "asset_type": asset_type,
            "category": f"{asset_type}_general",
            "status": random.choices(statuses, weights=status_weights)[0],
            "facility_id": random.choice(facility_ids),
            "serial_number": f"SN-{uuid.uuid4().hex[:8].upper()}",
            "_source_system": "synthetic",
            "_confidence": random.uniform(0.8, 1.0),
            "_classification": "UNCLASSIFIED",
        })
    
    return pd.DataFrame(records)


def generate_routes(config: dict, facilities: pd.DataFrame) -> pd.DataFrame:
    """Generate route data."""
    scenario = config.get("scenario", "baseline")
    facility_ids = facilities["id"].tolist()
    
    records = []
    route_id = 0
    
    for i, origin in enumerate(facility_ids):
        for dest in facility_ids[i+1:]:
            # Determine route type based on facility types
            route_type = "sea"  # Default
            
            # Determine access status
            access_status = "open"
            if scenario == "disrupted":
                # Taiwan Strait denial affects certain routes
                if origin in ["yokosuka", "kadena"] and dest in ["singapore", "subic"]:
                    access_status = "denied"
                elif origin in ["singapore", "subic"] and dest in ["yokosuka", "kadena"]:
                    access_status = "denied"
            
            records.append({
                "id": f"route_{route_id:03d}",
                "name": f"{origin.title()} to {dest.title()}",
                "origin_id": origin,
                "destination_id": dest,
                "distance_miles": random.randint(500, 5000),
                "typical_duration_hours": random.randint(24, 168),
                "route_type": route_type,
                "access_status": access_status,
                "risk_score": random.uniform(0.1, 0.5) if access_status == "open" else 0.9,
                "_source_system": "synthetic",
                "_confidence": 0.95,
                "_classification": "UNCLASSIFIED",
            })
            route_id += 1
    
    return pd.DataFrame(records)


def generate_communications(config: dict, facilities: pd.DataFrame) -> pd.DataFrame:
    """Generate communication data for Hume analysis."""
    count = config.get("counts", {}).get("communications", 1000)
    scenario = config.get("scenario", "baseline")
    
    # Adjust emotional distribution based on scenario
    if scenario == "disrupted":
        template_weights = {"normal": 0.3, "anxious": 0.35, "urgent": 0.25, "fearful": 0.1}
    else:
        template_weights = {"normal": 0.7, "anxious": 0.2, "urgent": 0.08, "fearful": 0.02}
    
    records = []
    facility_ids = facilities["id"].tolist()
    channels = ["email", "radio", "chat", "report"]
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        mood = random.choices(
            list(template_weights.keys()),
            weights=list(template_weights.values())
        )[0]
        
        content = random.choice(COMM_TEMPLATES[mood])
        
        records.append({
            "id": f"comm_{i:05d}",
            "content": content,
            "facility_id": random.choice(facility_ids),
            "sender": f"user_{random.randint(1, 50):03d}",
            "channel": random.choice(channels),
            "timestamp": (base_time + timedelta(minutes=random.randint(0, 43200))).isoformat(),
            "hume_status": "pending",
            "_source_system": "synthetic",
            "_confidence": 1.0,
            "_classification": "UNCLASSIFIED",
        })
    
    return pd.DataFrame(records)


def generate_chokepoints() -> pd.DataFrame:
    """Generate chokepoint data."""
    records = []
    for cp in CHOKEPOINTS:
        records.append({
            "id": cp["id"],
            "name": cp["name"],
            "latitude": cp["lat"],
            "longitude": cp["lon"],
            "strategic_importance": cp["importance"],
            "current_status": "open",
            "_source_system": "synthetic",
            "_confidence": 1.0,
            "_classification": "UNCLASSIFIED",
        })
    return pd.DataFrame(records)


def generate_all(scenario: str = "baseline", count_override: int = None):
    """Generate all synthetic data."""
    config = get_config()
    synthetic_config = config.get("synthetic_data", {})
    synthetic_config["scenario"] = scenario
    
    if count_override:
        for key in synthetic_config.get("counts", {}):
            synthetic_config["counts"][key] = count_override
    
    # Set random seed for reproducibility
    seed = synthetic_config.get("seed", 42)
    random.seed(seed)
    
    # Output directory
    paths = get_data_paths()
    output_dir = Path(paths.get("synthetic", "data/synthetic"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Generating synthetic data: scenario={scenario}, output={output_dir}")
    
    # Generate data
    facilities = generate_facilities(synthetic_config)
    facilities.to_parquet(output_dir / "facilities.parquet", index=False)
    logger.info(f"Generated {len(facilities)} facilities")
    
    assets = generate_assets(synthetic_config, facilities)
    assets.to_parquet(output_dir / "assets.parquet", index=False)
    logger.info(f"Generated {len(assets)} assets")
    
    routes = generate_routes(synthetic_config, facilities)
    routes.to_parquet(output_dir / "routes.parquet", index=False)
    logger.info(f"Generated {len(routes)} routes")
    
    communications = generate_communications(synthetic_config, facilities)
    communications.to_parquet(output_dir / "communications.parquet", index=False)
    logger.info(f"Generated {len(communications)} communications")
    
    chokepoints = generate_chokepoints()
    chokepoints.to_parquet(output_dir / "chokepoints.parquet", index=False)
    logger.info(f"Generated {len(chokepoints)} chokepoints")
    
    logger.info("Synthetic data generation complete")


if __name__ == "__main__":
    generate_all()
