#!/bin/bash
# Resume Parser Setup Script
# Run this script to quickly set up the project

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  Resume Parser - Quick Setup           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null || true

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p templates
echo "✅ Directories created"

# Check .env file
echo ""
echo "🔐 Checking configuration..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp -n .env.template .env 2>/dev/null || echo "" > .env
fi

if [ ! -f "config.yaml" ]; then
    echo "⚠️  config.yaml not found. Creating template..."
    cat > config.yaml << 'EOF'
OPENROUTER_API_KEY: "your_api_key_here"
EOF
fi

# API Key check
echo ""
echo "🔑 API Key Configuration"
echo "────────────────────────"

if [ ! -z "$OPENROUTER_API_KEY" ]; then
    echo "✅ OPENROUTER_API_KEY environment variable is set"
elif grep -q "your_api_key_here" config.yaml; then
    echo "⚠️  No API key configured yet"
    echo ""
    echo "To configure your API key, choose one option:"
    echo ""
    echo "  Option 1: Environment Variable (Recommended)"
    echo "    export OPENROUTER_API_KEY=\"sk-or-v1-your-key-here\""
    echo ""
    echo "  Option 2: Edit config.yaml"
    echo "    Replace 'your_api_key_here' with your actual key"
    echo ""
    echo "Get your free API key at: https://openrouter.ai/keys"
else
    echo "✅ API key appears to be configured"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                    ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure your API key (if not done):"
echo "   export OPENROUTER_API_KEY=\"sk-or-v1-your-key-here\""
echo ""
echo "2. Run the application:"
echo "   python app.py"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:8000"
echo ""
echo "4. (Optional) Run tests:"
echo "   python test_openrouter.py"
echo ""
echo "📚 Documentation: See README.md for more information"
echo ""
