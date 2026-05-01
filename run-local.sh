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

# .env must exist and contain a real API key (Claude or Gemini)
if [ ! -f .env ]; then
    echo "❌ .env file not found."
    echo ""
    echo "Create it with your API key, e.g.:"
    echo "  Claude: echo 'CLAUDE_API_KEY=sk-ant-your-key-here' > .env"
    echo "  Gemini: printf 'AI_PROVIDER=gemini\nGEMINI_API_KEY=your-key\n' > .env"
    exit 1
fi

if grep -q "your.*key.*here\|your_claude_api_key\|your_gemini_api_key" .env 2>/dev/null; then
    echo "❌ Please replace the placeholder in .env with your real API key."
    exit 1
fi

HAS_VALID_KEY=false
if grep -qE "^CLAUDE_API_KEY=sk-ant-.{5}" .env 2>/dev/null; then
    HAS_VALID_KEY=true
fi
if grep -qE "^GEMINI_API_KEY=.{10}" .env 2>/dev/null; then
    HAS_VALID_KEY=true
fi

if [ "$HAS_VALID_KEY" = "false" ]; then
    echo "❌ No valid API key found in .env."
    echo ""
    echo "Add one of the following:"
    echo "  CLAUDE_API_KEY=sk-ant-your-key-here"
    echo "  GEMINI_API_KEY=your-gemini-key-here  (also set AI_PROVIDER=gemini)"
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
