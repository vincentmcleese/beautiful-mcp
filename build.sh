#!/bin/bash
set -e

echo "🚀 Building Beautiful Gradient MCP for Railway..."
echo "================================================"

# Check if frontend directory exists
if [ ! -d "beautiful_gradient_mcp/frontend" ]; then
    echo "❌ Error: Frontend directory not found"
    exit 1
fi

# Build frontend
echo ""
echo "📦 Building frontend..."
cd beautiful_gradient_mcp/frontend

if [ ! -f "package.json" ]; then
    echo "❌ Error: Frontend package.json not found"
    exit 1
fi

npm install
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Frontend built successfully!"
echo ""
echo "Build artifacts:"
ls -lh dist/

cd ../..

echo ""
echo "================================================"
echo "✅ Build completed successfully!"
echo "Python dependencies installed by Railway from requirements.txt"
