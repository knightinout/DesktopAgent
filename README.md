# Desktop Agent

**Chat with an AI to install software on Linux — just type what you want.**

> "Install Firefox" → the agent figures out the commands, runs them, and confirms it worked.

Demo video: https://youtu.be/uwGJwdlxXp4

---

## What it does

You open a chat window in your browser, type something like *"Install GIMP image editor"* or *"Set up a Python development environment"*, and the AI handles the rest — finding the right package, running the install commands, checking for errors, and retrying automatically if something goes wrong.

---

## Before you start

You need:

- **An AI API key** (pick one — both have free tiers):
  - **Gemini (Google):** https://aistudio.google.com/ — free, no billing required
  - **Claude (Anthropic):** https://console.anthropic.com/ — free tier available
- **Python 3.10 or newer** — check with `python3 --version`
- **Docker** — only needed if you want to see a live desktop alongside the chat (optional)

---

## Getting started

### Step 1 — Download the project

```bash
git clone https://github.com/knightinout/DesktopAgent.git
cd DesktopAgent
```

### Step 2 — Run the launcher

```bash
./start.sh
```

On first run it will ask which AI provider you want to use and prompt you to paste your API key. It saves everything automatically. After that, just open your browser at:

```
http://localhost:8000
```

Type a message like *"Install VLC"* and watch the agent work.

---

## Running modes

The launcher (`./start.sh`) offers three modes. Here's what they actually mean:

| Mode | What you see | Requires Docker? |
|------|-------------|-----------------|
| **Web chat + live desktop** | Chat panel on the left, a full Linux desktop on the right — you can watch apps launch in real time | Yes |
| **Web chat only** | Just the chat panel in your browser — the AI still installs things, you just don't see the desktop | No |
| **Classic GUI** | A simple desktop app instead of a browser interface | Yes |

**On Windows (WSL2) or a VM with no Docker?** Choose the "web chat only" mode — it works everywhere and needs nothing extra installed.

---

## Common commands

```bash
# Start the agent (recommended — handles everything)
./start.sh

# Start web chat only, no Docker needed
./run-local.sh

# Stop the agent (if running in Docker)
docker stop agent-chatbot

# View logs if something seems stuck
docker logs -f agent-chatbot
```

---

## API key setup

### Option A — Gemini (Google)

1. Go to https://aistudio.google.com/
2. Sign in with a Google account
3. Click **Get API key** → **Create API key**
4. Copy the key and paste it when `./start.sh` asks

### Option B — Claude (Anthropic)

1. Go to https://console.anthropic.com/
2. Create an account and go to **API Keys**
3. Click **Create Key**, copy it (starts with `sk-ant-`)
4. Paste it when `./start.sh` asks

### Adding keys directly to `.env`

You can skip the interactive setup entirely by editing `.env` yourself. Create or edit it in the project folder:

```bash
# Both keys can live in the same file
CLAUDE_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=your-gemini-key-here

# Set which one to use (optional — if only one key is present it's used automatically)
AI_PROVIDER=gemini
```

When you run `./start.sh`:
- **One key in `.env`** → used automatically, no questions asked
- **Both keys in `.env`** → you're asked which provider to use that session
- **No keys** → guided setup prompts you to paste one

---

## Troubleshooting

### "No .env file" or "API key not found"

Run `./start.sh` — it will create the file for you. Or create it manually:

```bash
# Gemini example
echo "AI_PROVIDER=gemini" > .env
echo "GEMINI_API_KEY=your-key-here" >> .env

# Claude example
echo "CLAUDE_API_KEY=sk-ant-your-key-here" > .env
```

---

### Running on Windows (via WSL2)

WSL2 is a way to run Linux inside Windows. If you're using it:

**Easiest setup — web chat only, no Docker:**
```bash
./run-local.sh
```
Then open `http://localhost:8000` in your **Windows** browser. This works without any extra setup.

**If you want Docker too:**
- Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) and enable the WSL2 backend in its settings
- After that, `./start.sh` and `http://localhost:8000` work in your Windows browser automatically

If `localhost` doesn't connect, find your WSL2 IP and use that instead:
```bash
ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
# Then open http://<that-ip>:8000 in Windows browser
```

---

### "Port 8000 is already in use"

Something else is running on that port. Find and stop it:

```bash
# Find what's using port 8000
lsof -i :8000

# Stop it (replace <PID> with the number shown)
kill <PID>
```

---

### "Docker not found" or Docker errors

If Docker isn't installed or not running, use the no-Docker mode instead:

```bash
./run-local.sh
```

To install Docker on Ubuntu:
```bash
sudo apt install docker.io
sudo usermod -aG docker $USER
# Log out and back in, then try again
```

---

### The agent seems stuck or gave a wrong answer

- Check the logs: `docker logs -f agent-chatbot`
- Try rephrasing your request — be specific, e.g. *"Install the docker.io package using apt"* instead of just *"Install Docker"*
- Restart: `docker stop agent-chatbot` then `./start.sh`

---

## Stopping the agent

```bash
# If you started with run-chatbot.sh or start.sh (Docker mode)
docker stop agent-chatbot

# If you started with run-local.sh
Press Ctrl-C in the terminal
```

---

## License

See `LICENSE` file.
