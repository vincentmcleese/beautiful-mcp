#!/bin/bash

# Beautiful Gradient MCP - Deployment Build Script
# This script builds the frontend and prepares for deployment

set -e  # Exit on error

echo "🚀 Beautiful Gradient MCP - Build for Deployment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from beautiful_gradient_mcp directory"
    exit 1
fi

# Build frontend
echo ""
echo "📦 Building frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

echo "🔨 Building React app..."
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Frontend built successfully"
cd ..

# Check Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo "✅ Requirements file found"

# Summary
echo ""
echo "=================================================="
echo "✅ Build completed successfully!"
echo ""
echo "📁 Deployment artifacts:"
echo "   - Frontend: frontend/dist/"
echo "   - Backend: main.py"
echo "   - Dependencies: requirements.txt"
echo ""
echo "🚂 Ready for Railway deployment!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub"
echo "2. Connect repository to Railway"
echo "3. Set environment variables in Railway dashboard"
echo "4. Deploy! 🎉"
echo ""
echo "For detailed instructions, see RAILWAY_DEPLOYMENT.md"
echo "=================================================="
