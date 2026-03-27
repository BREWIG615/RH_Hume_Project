"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_facility():
    """Return sample facility data."""
    return {
        "id": "test_facility",
        "name": "Test Facility",
        "facility_type": "warehouse",
        "latitude": 35.0,
        "longitude": 139.0,
        "operational_status": "operational",
    }


@pytest.fixture
def sample_asset():
    """Return sample asset data."""
    return {
        "id": "test_asset",
        "name": "Test Asset",
        "asset_type": "truck",
        "status": "FMC",
        "facility_id": "test_facility",
    }


@pytest.fixture
def sample_communication():
    """Return sample communication data."""
    return {
        "id": "test_comm",
        "content": "Worried about the supply chain delays affecting our operations.",
        "facility_id": "test_facility",
        "channel": "email",
    }
