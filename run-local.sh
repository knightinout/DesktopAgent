#!/bin/bash
# Desktop Agent - Local mode (no Docker, no VNC)
# Works on plain Linux, WSL2, and any environment where Docker is unavailable.
# The AI chatbot runs directly on your machine; the VNC desktop panel will be
# empty (no desktop environment is started).

set -e

echo "🤖 Desktop Agent - Local Mode (no Docker)"
echo "==========================================="
echo ""

# ── Preflight checks ────────────────────────────────────────────────────────

# .env must exist and contain a real API key
if [ ! -f .env ]; then
    echo "❌ .env file not found."
    echo ""
    echo "Create it with your Claude API key:"
    echo "  echo 'CLAUDE_API_KEY=sk-ant-your-key-here' > .env"
    exit 1
fi

if grep -q "your.*key.*here\|your_claude_api_key" .env 2>/dev/null; then
    echo "❌ Please replace the placeholder in .env with your real CLAUDE_API_KEY."
    exit 1
fi

echo "✅ API key found"

# Python 3.10+ required
if ! command -v python3 &>/dev/null; then
    echo "❌ python3 not found. Install Python 3.10+ first."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(sys.version_info >= (3,10))")
if [ "$PY_VER" != "True" ]; then
    echo "❌ Python 3.10+ required (found $(python3 --version))."
    exit 1
fi

echo "✅ Python OK ($(python3 --version))"

# ── Virtual environment ──────────────────────────────────────────────────────

if [ ! -d venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing / verifying dependencies..."
pip install -q -r requirements.txt

echo "✅ Dependencies ready"
echo ""

# ── Port availability ────────────────────────────────────────────────────────

if lsof -i :8000 &>/dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use. Stop the existing process or change the port."
    exit 1
fi

# ── Launch ───────────────────────────────────────────────────────────────────

echo "🚀 Starting chatbot server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Open in your browser:"
echo "  👉 http://localhost:8000"
echo ""
echo "  Note: The VNC desktop panel will be empty"
echo "  (no desktop environment in local mode)."
echo "  The AI chatbot works fully."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl-C to stop."
echo ""

python3 chatbot.py
