#!/bin/bash
set -e

echo "Building Beautiful Gradient MCP for Railway..."

# Build frontend
echo "Building frontend..."
cd beautiful_gradient_mcp/frontend
npm install
npm run build
cd ../..

echo "Frontend built successfully!"
echo "Python dependencies will be installed by Railway from requirements.txt"
