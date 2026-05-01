#!/bin/bash
# DesktopAgent - Unified Launcher
# Runs AI-powered installation assistant in Docker with VNC desktop

set -e

echo "🤖 DesktopAgent - AI Installation Assistant"
echo "==========================================="
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please create .env with your API key:"
    echo "  Claude: echo 'CLAUDE_API_KEY=sk-ant-your-key-here' > .env"
    echo "  Gemini: printf 'AI_PROVIDER=gemini\nGEMINI_API_KEY=your-key\n' > .env"
    exit 1
fi

if grep -q "your.*key.*here" .env 2>/dev/null; then
    echo "❌ Please replace the placeholder in .env with your real API key."
    exit 1
fi

echo "✅ API key configured"
echo ""

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t desktop-agent .

# Stop existing container
docker stop desktop-agent-running 2>/dev/null || true

echo ""
echo "🚀 Starting Desktop Agent container..."

# Run container
docker run -d --rm \
    --name desktop-agent-running \
    -p 5901:5901 \
    -v "$(pwd)/.env:/app/.env:ro" \
    -v "$(pwd)/logs:/app/logs" \
    desktop-agent

sleep 5

echo "✅ Container started!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📺 VNC Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Try to auto-connect with VNC viewer
if command -v vncviewer &> /dev/null; then
    echo "🔌 Launching VNC viewer..."
    echo ""
    echo "Password: password"
    echo ""
    # Launch VNC viewer (will prompt for password)
    (vncviewer localhost:5901 &> /dev/null &)
    sleep 1
    echo "✅ VNC viewer launched!"
    echo "   (Enter password: password)"
    echo ""
elif command -v xtigervncviewer &> /dev/null; then
    echo "🔌 Launching TigerVNC viewer..."
    echo ""
    echo "Password: password"
    echo ""
    (xtigervncviewer localhost:5901 &> /dev/null &)
    sleep 1
    echo "✅ VNC viewer launched!"
    echo "   (Enter password: password)"
    echo ""
elif command -v remmina &> /dev/null; then
    echo "🔌 Launching Remmina VNC viewer..."
    echo ""
    (remmina -c vnc://localhost:5901 &> /dev/null &)
    sleep 1
    echo "✅ Remmina launched!"
    echo "   (Enter password: password)"
    echo ""
else
    echo "No VNC viewer found. Install one:"
    echo ""
    echo "  sudo apt install tigervnc-viewer"
    echo "  # OR"
    echo "  sudo apt install remmina"
    echo ""
    echo "Then connect manually:"
    echo "  vncviewer localhost:5901"
    echo "  Password: password"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 What You'll See:"
echo ""
echo "  1. XFCE Desktop with DesktopAgent GUI"
echo "  2. Demo installation guide auto-loaded"
echo "  3. Click '▶ Start Installation' to begin"
echo "  4. Watch as apps get installed automatically!"
echo ""
echo "🛑 To stop:"
echo "   docker stop desktop-agent-running"
echo ""
echo "📊 View logs:"
echo "   docker logs -f desktop-agent-running"
echo "   tail -f logs/guide_executor.log"
echo ""
