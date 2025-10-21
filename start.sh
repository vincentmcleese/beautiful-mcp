#!/bin/bash
set -e

echo "🚀 Starting Beautiful Gradient MCP Server..."

# Build frontend if not already built (first deploy or after clean)
if [ ! -d "beautiful_gradient_mcp/frontend/dist" ]; then
    echo "⚠️  Frontend not built, building now..."
    bash build.sh
else
    echo "✅ Frontend already built, skipping build step"
fi

# Start the server
echo "🌐 Starting uvicorn server..."
cd beautiful_gradient_mcp && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
