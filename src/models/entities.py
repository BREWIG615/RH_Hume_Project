"""
Domain Models

Core entity models and enumerations for the logistics platform.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# =============================================================================
# Enumerations
# =============================================================================

class AssetStatus(str, Enum):
    """Asset readiness status codes."""
    FMC = "FMC"      # Fully Mission Capable
    PMCM = "PMCM"    # Partially Mission Capable - Maintenance
    PMCS = "PMCS"    # Partially Mission Capable - Supply
    NMCM = "NMCM"    # Not Mission Capable - Maintenance
    NMCS = "NMCS"    # Not Mission Capable - Supply


class AssetType(str, Enum):
    """Asset type categories."""
    TRUCK = "truck"
    AIRCRAFT = "aircraft"
    VESSEL = "vessel"
    CONTAINER = "container"
    EQUIPMENT = "equipment"


class FacilityType(str, Enum):
    """Facility type categories."""
    WAREHOUSE = "warehouse"
    PORT = "port"
    AIRFIELD = "airfield"
    DEPOT = "depot"
    BASE = "base"


class RouteAccessStatus(str, Enum):
    """Route access status."""
    OPEN = "open"
    RESTRICTED = "restricted"
    DENIED = "denied"
    UNKNOWN = "unknown"


class DisruptionStatus(str, Enum):
    """Disruption lifecycle status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"


class WorkOrderStatus(str, Enum):
    """Work order status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_PARTS = "awaiting_parts"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReviewItemStatus(str, Enum):
    """Review item status."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class HumeProcessingStatus(str, Enum):
    """Hume processing status for communications."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    FLAG = "flag"
    ALERT = "alert"
    ESCALATE = "escalate"


# =============================================================================
# Base Provenance Mixin
# =============================================================================

@dataclass
class ProvenanceMixin:
    """Standard provenance fields for all entities."""
    _source_system: str = "synthetic"
    _source_record_id: Optional[str] = None
    _ingested_at: datetime = field(default_factory=datetime.now)
    _confidence: float = 1.0
    _classification: str = "UNCLASSIFIED"


# =============================================================================
# Core Entities
# =============================================================================

@dataclass
class Facility(ProvenanceMixin):
    """Logistics facility."""
    id: str = ""
    name: str = ""
    facility_type: FacilityType = FacilityType.WAREHOUSE
    capabilities: list[str] = field(default_factory=list)
    latitude: float = 0.0
    longitude: float = 0.0
    region_id: Optional[str] = None
    operational_status: str = "operational"


@dataclass
class Asset(ProvenanceMixin):
    """Logistics asset."""
    id: str = ""
    name: str = ""
    asset_type: AssetType = AssetType.EQUIPMENT
    category: str = ""
    status: AssetStatus = AssetStatus.FMC
    facility_id: Optional[str] = None
    serial_number: Optional[str] = None


@dataclass
class Route(ProvenanceMixin):
    """Transportation route."""
    id: str = ""
    name: str = ""
    origin_id: str = ""
    destination_id: str = ""
    distance_miles: float = 0.0
    typical_duration_hours: float = 0.0
    route_type: str = "sea"
    access_status: RouteAccessStatus = RouteAccessStatus.OPEN
    risk_score: float = 0.0


@dataclass
class Chokepoint(ProvenanceMixin):
    """Strategic chokepoint."""
    id: str = ""
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    strategic_importance: str = "high"
    current_status: RouteAccessStatus = RouteAccessStatus.OPEN


@dataclass
class Communication(ProvenanceMixin):
    """Communication for Hume analysis."""
    id: str = ""
    content: str = ""
    facility_id: Optional[str] = None
    sender: Optional[str] = None
    channel: str = "email"
    timestamp: datetime = field(default_factory=datetime.now)
    hume_status: HumeProcessingStatus = HumeProcessingStatus.PENDING
    hume_anxiety: float = 0.0
    hume_urgency: float = 0.0
    hume_confusion: float = 0.0
    hume_fear: float = 0.0


@dataclass
class ReviewItem(ProvenanceMixin):
    """Item requiring human review."""
    id: str = ""
    item_type: str = ""
    status: ReviewItemStatus = ReviewItemStatus.PENDING
    priority: float = 0.5
    severity: AlertSeverity = AlertSeverity.ALERT
    reason: str = ""
    entity_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
