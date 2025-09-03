#!/bin/bash

# Quick Start Script for Energy Trading System
# This script helps you get the system running quickly

set -e

echo "⚡ Energy Trading System - Quick Start ⚡"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 9 ]]; then
    echo "❌ Python 3.9+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Node.js is installed (for CDK)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION detected"
    
    # Install Node.js dependencies
    echo "📥 Installing Node.js dependencies..."
    npm install
else
    echo "⚠️  Node.js not detected. CDK deployment will not be available."
    echo "   You can still run the local demo without AWS infrastructure."
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run the local demo:"
echo "   python scripts/demo.py"
echo ""
echo "2. Or run the full simulation:"
echo "   python scripts/run_simulation.py --duration 10"
echo ""
echo "3. To deploy AWS infrastructure (requires AWS credentials):"
echo "   cd infrastructure/cdk"
echo "   cdk deploy"
echo ""
echo "4. View the README.md for more detailed instructions"
echo ""

# Ask if user wants to run the demo now
read -p "Would you like to run the demo now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting demo..."
    python scripts/demo.py
fi

echo ""
echo "✨ Quick start completed! Check the logs above for any issues."
echo "   For help, see README.md or create an issue on GitHub."
