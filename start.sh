#!/bin/bash
# Desktop Agent - Smart Launcher
# Single entry-point: handles first-run .env setup and auto-selects run mode.

set -e

echo "Desktop Agent - Smart Launcher"
echo "================================"
echo ""

# ── 1. .env setup ─────────────────────────────────────────────────────────────

HAS_VALID_KEY=false

if [ -f .env ]; then
    if grep -qE "^CLAUDE_API_KEY=sk-ant-.{5}" .env 2>/dev/null; then
        HAS_VALID_KEY=true
    fi
    if grep -qE "^GEMINI_API_KEY=.{10}" .env 2>/dev/null; then
        HAS_VALID_KEY=true
    fi
fi

if [ "$HAS_VALID_KEY" = "false" ]; then
    echo "First-time setup: AI API key required."
    echo ""
    echo "Which AI provider do you want to use?"
    echo "  [1] Claude (Anthropic)  — https://console.anthropic.com/"
    echo "  [2] Gemini (Google)     — https://aistudio.google.com/"
    echo ""
    printf "Provider [default: 1]: "
    read -r PROVIDER_CHOICE
    PROVIDER_CHOICE="${PROVIDER_CHOICE:-1}"
    echo ""

    # Preserve WATCH_FOLDER from existing .env if present
    WATCH_LINE=""
    if [ -f .env ]; then
        WATCH_LINE=$(grep "^WATCH_FOLDER=" .env 2>/dev/null || true)
    fi

    if [ "$PROVIDER_CHOICE" = "2" ]; then
        printf "Paste your GEMINI_API_KEY: "
        read -r API_KEY
        echo ""
        if [ -z "$API_KEY" ]; then
            echo "No key entered. Exiting."
            exit 1
        fi
        { printf "AI_PROVIDER=gemini\nGEMINI_API_KEY=%s\n" "$API_KEY"; [ -n "$WATCH_LINE" ] && printf "%s\n" "$WATCH_LINE"; } > .env
        echo "Gemini API key saved to .env"
    else
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
        { printf "AI_PROVIDER=claude\nCLAUDE_API_KEY=%s\n" "$API_KEY"; [ -n "$WATCH_LINE" ] && printf "%s\n" "$WATCH_LINE"; } > .env
        echo "Claude API key saved to .env"
    fi
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
