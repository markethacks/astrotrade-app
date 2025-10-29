#!/bin/bash

# AstroTrade Personal Assistant - Setup Script
# This script automates the setup process

echo "🌙 AstroTrade Personal Assistant - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if (( $(echo "$python_version >= $required_version" | bc -l) )); then
    echo "✅ Python $python_version detected (required: $required_version+)"
else
    echo "❌ Python $required_version or higher is required. Current: $python_version"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p sweph outputs data

# Check for Swiss Ephemeris files
echo ""
echo "📊 Checking Swiss Ephemeris files..."
if [ ! -f "sweph/seas_18.se1" ] || [ ! -f "sweph/semo_18.se1" ] || [ ! -f "sweph/sepl_18.se1" ]; then
    echo "⚠️  Swiss Ephemeris files not found. Downloading..."
    
    cd sweph
    
    # Download ephemeris files
    wget -q https://www.astro.com/ftp/swisseph/ephe/seas_18.se1
    wget -q https://www.astro.com/ftp/swisseph/ephe/semo_18.se1
    wget -q https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1
    
    cd ..
    
    if [ -f "sweph/seas_18.se1" ] && [ -f "sweph/semo_18.se1" ] && [ -f "sweph/sepl_18.se1" ]; then
        echo "✅ Swiss Ephemeris files downloaded"
    else
        echo "❌ Failed to download Swiss Ephemeris files"
        echo "   Please download manually from: https://www.astro.com/ftp/swisseph/ephe/"
        echo "   Required files: seas_18.se1, semo_18.se1, sepl_18.se1"
        echo "   Place them in the sweph/ directory"
    fi
else
    echo "✅ Swiss Ephemeris files found"
fi

# Check configuration files
echo ""
echo "⚙️  Checking configuration files..."

if [ -f "profiles.json" ]; then
    echo "✅ profiles.json found"
else
    echo "⚠️  profiles.json not found (should exist)"
fi

if [ -f "config.json" ]; then
    echo "✅ config.json found"
else
    echo "⚠️  config.json not found (should exist)"
fi

# Setup complete
echo ""
echo "================================================"
echo "🎉 Setup Complete!"
echo "================================================"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo ""
echo "Or simply run: ./run.sh"
echo ""
echo "For more information, see README.md"
echo ""

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run app.py
EOF

chmod +x run.sh

echo "✅ Created run.sh script for easy launching"
echo ""
