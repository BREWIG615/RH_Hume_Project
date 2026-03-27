"""Tests for domain models."""

import pytest
from src.models.entities import AssetStatus, Asset, Facility


def test_asset_status_enum():
    """Test asset status enumeration."""
    assert AssetStatus.FMC.value == "FMC"
    assert AssetStatus.NMCS.value == "NMCS"


def test_asset_creation():
    """Test asset model creation."""
    asset = Asset(id="test", name="Test Asset", status=AssetStatus.FMC)
    assert asset.id == "test"
    assert asset.status == AssetStatus.FMC


def test_facility_creation():
    """Test facility model creation."""
    facility = Facility(id="test", name="Test Facility")
    assert facility.id == "test"
    assert facility._confidence == 1.0
