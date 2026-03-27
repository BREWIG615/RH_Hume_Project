#!/bin/bash
# Verify development environment

echo "=== RH Hume Project Environment Check ==="
echo ""

# Check Python
echo -n "Python: "
python3 --version 2>/dev/null || echo "NOT FOUND"

# Check Docker/Podman
echo -n "Container runtime: "
if command -v podman &> /dev/null; then
    podman --version
elif command -v docker &> /dev/null; then
    docker --version
else
    echo "NOT FOUND"
fi

# Check compose
echo -n "Compose: "
if command -v podman-compose &> /dev/null; then
    podman-compose --version
elif command -v docker &> /dev/null; then
    docker compose version
else
    echo "NOT FOUND"
fi

# Check API keys
echo ""
echo "=== API Keys ==="
[ -n "$CLAUDE_API_KEY" ] && echo "CLAUDE_API_KEY: Set" || echo "CLAUDE_API_KEY: NOT SET"
[ -n "$HUME_API_KEY" ] && echo "HUME_API_KEY: Set" || echo "HUME_API_KEY: NOT SET"
[ -n "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY: Set" || echo "OPENAI_API_KEY: NOT SET"

# Check .env file
echo ""
echo "=== Configuration ==="
[ -f "docker/.env" ] && echo ".env file: Present" || echo ".env file: NOT FOUND (copy from .env.example)"

echo ""
echo "=== Done ==="
