#!/bin/bash
# Reset demo environment to clean state

set -e

echo "=== Resetting Demo Environment ==="

# Stop services
echo "Stopping services..."
cd docker
docker compose down -v 2>/dev/null || podman-compose down -v 2>/dev/null || true
cd ..

# Clean data directories
echo "Cleaning data..."
rm -rf data/raw/* data/processed/* data/presentation/* data/synthetic/*

# Start services
echo "Starting services..."
cd docker
docker compose up -d || podman-compose up -d
cd ..

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Initialize
echo "Initializing..."
make init

# Generate data
echo "Generating demo data..."
make generate-data

# Run pipeline
echo "Running pipeline..."
make run-pipeline

# Health check
echo ""
make check-health

echo ""
echo "=== Demo Reset Complete ==="
