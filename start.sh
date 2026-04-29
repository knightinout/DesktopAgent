#!/bin/bash
# Desktop Agent - Smart Launcher
# Single entry-point: handles first-run .env setup and auto-selects run mode.

set -e

echo "Desktop Agent - Smart Launcher"
echo "================================"
echo ""

# ── 1. .env setup ─────────────────────────────────────────────────────────────

NEEDS_KEY=false

if [ ! -f .env ]; then
    NEEDS_KEY=true
elif grep -q "your.*key.*here\|your_claude_api_key\|sk-ant-your" .env 2>/dev/null; then
    NEEDS_KEY=true
elif ! grep -q "CLAUDE_API_KEY=sk-ant-" .env 2>/dev/null; then
    NEEDS_KEY=true
fi

if [ "$NEEDS_KEY" = "true" ]; then
    echo "First-time setup: Claude API key required."
    echo ""
    echo "Get your key at: https://console.anthropic.com/"
    echo ""
    printf "Paste your CLAUDE_API_KEY (starts with sk-ant-): "
    read -r API_KEY
    echo ""

    if [ -z "$API_KEY" ]; then
        echo "No key entered. Exiting."
        exit 1
    fi

    if [[ "$API_KEY" != sk-ant-* ]]; then
        echo "Warning: key does not start with 'sk-ant-' — saving anyway."
    fi

    echo "CLAUDE_API_KEY=$API_KEY" > .env
    echo "API key saved to .env"
    echo ""
fi

echo "API key: OK"
echo ""

# ── 2. Detect Docker ───────────────────────────────────────────────────────────

DOCKER_AVAILABLE=false
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    DOCKER_AVAILABLE=true
fi

# ── 3. Auto-select default mode ───────────────────────────────────────────────

if [ "$DOCKER_AVAILABLE" = "true" ]; then
    DEFAULT=1
    DOCKER_STATUS="available"
else
    DEFAULT=2
    DOCKER_STATUS="not available — local mode will be used"
fi

# ── 4. Show menu ───────────────────────────────────────────────────────────────

echo "Docker: $DOCKER_STATUS"
echo ""
echo "How do you want to run Desktop Agent?"
echo ""
echo "  [1] Web chatbot + XFCE desktop  (Docker) — chat + live desktop in browser"
if [ "$DEFAULT" = "1" ]; then
    echo "      ^ auto-selected"
fi
echo "  [2] Web chatbot only            (local Python, no Docker)"
if [ "$DEFAULT" = "2" ]; then
    echo "      ^ auto-selected (Docker not available)"
fi
echo "  [3] Classic VNC desktop GUI     (Docker) — original tkinter interface"
echo ""
printf "Choice [default: %d]: " "$DEFAULT"
read -r CHOICE
CHOICE="${CHOICE:-$DEFAULT}"
echo ""

# ── 5. Delegate ────────────────────────────────────────────────────────────────

case "$CHOICE" in
    1)
        if [ "$DOCKER_AVAILABLE" = "false" ]; then
            echo "Docker is not available. Please install Docker to use this mode."
            echo "Falling back to local mode..."
            echo ""
            exec ./run-local.sh
        fi
        exec ./run-chatbot.sh
        ;;
    2)
        exec ./run-local.sh
        ;;
    3)
        if [ "$DOCKER_AVAILABLE" = "false" ]; then
            echo "Docker is not available. Please install Docker to use this mode."
            exit 1
        fi
        exec ./run.sh
        ;;
    *)
        echo "Invalid choice: $CHOICE. Exiting."
        exit 1
        ;;
esac
