#!/bin/bash
# Ubuntu Installation Script for Desktop Agent
# Supports Ubuntu 20.04+, XFCE, GNOME, KDE

set -e  # Exit on any error

echo "🚀 Installing Desktop Agent for Ubuntu Linux..."

# Check Ubuntu version
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "❌ This script is designed for Ubuntu. Other distros may work but are unsupported."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    git \
    curl \
    wget \
    docker.io \
    xauth \
    pulseaudio \
    dbus-x11

# Add user to docker group (requires logout/login to take effect)
echo "🐳 Adding user to docker group..."
sudo usermod -aG docker $USER

# Create application directory
APP_DIR="$HOME/.local/share/desktop-agent"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Clone or copy application
if [ -d ".git" ]; then
    echo "📋 Installing from local repository..."
    cp -r . "$APP_DIR/"
else
    echo "📋 Cloning from GitHub..."
    git clone https://github.com/knightinout/DesktopAgent.git "$APP_DIR"
fi

cd "$APP_DIR"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create desktop entry
echo "🖥️ Creating desktop entry..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/desktop-agent.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Desktop Agent
Comment=AI-powered desktop assistant for file organization and automation
Exec=$APP_DIR/venv/bin/python $APP_DIR/main.py
Icon=$APP_DIR/assets/icon.png
Terminal=false
StartupNotify=true
Categories=Utility;System;FileManager;
Keywords=ai;assistant;automation;files;
StartupWMClass=desktop-agent
EOF

# Make desktop entry executable
chmod +x "$HOME/.local/share/applications/desktop-agent.desktop"

# Create configuration template
echo "⚙️ Setting up configuration..."
if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << EOF
# Desktop Agent Configuration
# Choose provider: claude (default) or gemini
AI_PROVIDER=claude

# Claude (Anthropic) key — https://console.anthropic.com/
CLAUDE_API_KEY=your_claude_api_key_here

# Gemini (Google) key — https://aistudio.google.com/ (free tier)
# Set AI_PROVIDER=gemini above to use Gemini instead.
GEMINI_API_KEY=your_gemini_api_key_here

WATCH_FOLDER=$HOME/Downloads
LOG_LEVEL=INFO
EOF
    echo "📝 Created .env template at $APP_DIR/.env"
    echo "📝 Please edit $APP_DIR/.env and add your Claude or Gemini API key"
fi

# Create launcher script
echo "🚀 Creating launcher script..."
cat > "$HOME/.local/bin/desktop-agent" << EOF
#!/bin/bash
cd "$APP_DIR"
source venv/bin/activate
python main.py "\$@"
EOF

mkdir -p "$HOME/.local/bin"
chmod +x "$HOME/.local/bin/desktop-agent"

echo ""
echo "✅ Desktop Agent installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit $APP_DIR/.env and add your Claude or Gemini API key"
echo "2. Log out and log back in (for Docker group membership)"
echo "3. Launch from applications menu or run: desktop-agent"
echo ""
echo "🐳 Docker sandbox testing:"
echo "   docker run -it --rm -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ubuntu:latest"
echo ""
echo "📚 Documentation: https://github.com/knightinout/DesktopAgent#readme"