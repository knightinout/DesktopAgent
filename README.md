# 🤖 Desktop Agent

# Video 
https://youtu.be/uwGJwdlxXp4

**AI-Powered Installation Assistant for Linux**

An intelligent desktop assistant that automates software installation using Claude AI. Choose between a modern web interface or the original VNC desktop environment.

---

## 🚀 Quick Start

### **Recommended: One command to get started**

```bash
./start.sh
```

`start.sh` is the single entry-point that:
- Prompts for your Claude API key on first run and saves it to `.env`
- Detects whether Docker is available and auto-selects the best mode
- Offers a simple menu so you can override the default

```
  [1] Web chatbot + XFCE desktop  (Docker) — chat + live desktop in browser
  [2] Web chatbot only            (local Python, no Docker)
  [3] Classic VNC desktop GUI     (Docker) — original tkinter interface
```

Get your API key at: https://console.anthropic.com/

---

### **Running scripts directly**

#### Web Chatbot + XFCE Desktop (Docker)

Modern web interface with AI chatbot and XFCE desktop side-by-side in the browser:

```bash
# Requires .env with CLAUDE_API_KEY
./run-chatbot.sh
# http://localhost:8000
```

**What you get:**
- **Left panel**: AI chatbot to install apps
- **Right panel**: XFCE desktop via noVNC — launch and test apps
- **All in one browser window!**

#### Local Mode (no Docker — great for WSL2 / VMs)

Runs the AI chatbot directly on your machine. No Docker or desktop environment needed:

```bash
./run-local.sh
# http://localhost:8000
```

#### Original VNC Desktop GUI (Docker)

Classic tkinter GUI inside an XFCE desktop, accessed through a VNC viewer:

```bash
./run.sh
# VNC viewer auto-connects to localhost:5901
```

---

## ✨ Features

### Web Chatbot Interface
- ✅ **Split-screen design** - Chat left, desktop right
- ✅ **Web-based VNC** - No separate VNC client needed
- ✅ **LangChain agent** - Autonomous reasoning and tool use
- ✅ **Real-time viewing** - Watch apps install and launch
- ✅ **Docker isolated** - Safe testing environment

### Original Interface
- ✅ **Classic GUI** - Tkinter-based desktop application
- ✅ **Guide execution** - Parses installation text files
- ✅ **VNC desktop** - Full XFCE environment
- ✅ **Step-by-step** - Manual control over execution

---

## 🛠️ Tech Stack

- **AI**: Claude Sonnet-4 via Anthropic API
- **Agent Framework**: LangChain (web interface)
- **GUI**: Python tkinter + XFCE desktop (original)
- **Web**: FastAPI + noVNC (web interface)
- **Container**: Docker with VNC server
- **Security**: Command validation & sandboxing

---

## 📁 Project Structure

```
DesktopAgent/
├── start.sh                  # ⭐ Primary entry-point (smart launcher)
├── chatbot.py                # ⭐ Web chatbot interface
├── Dockerfile.chatbot        # ⭐ Web chatbot Docker config
├── run-chatbot.sh            # Web chatbot launcher (Docker + XFCE)
├── run-local.sh              # Local Python launcher (no Docker)
│
├── agents/
│   ├── desktop_agent.py      # LangChain agent (ReAct)
│   ├── langchain_tools.py    # Agent tools
│   ├── autonomous_mode.py    # Auto-execution
│   └── file_organizer.py     # File categorization
│
├── utils/
│   ├── guide_parser.py       # Installation guide parser
│   ├── guide_executor.py     # Step execution engine
│   ├── security.py           # Command validation
│   └── claude_client.py      # Claude API client
│
├── gui/
│   └── app.py                # Original GUI
│
├── Dockerfile                # Original desktop environment
├── run.sh                    # Original launcher
├── main.py                   # Original entry point
└── requirements.txt          # Python dependencies
```

---

## 🎯 Usage Examples

### Web Chatbot Interface

1. **Open browser**: http://localhost:8000
2. **Install apps** (left panel):
   ```
   Install GIMP image editor
   Install Firefox browser
   Install VLC media player
   ```
3. **Launch apps** (right panel - VNC):
   ```bash
   gimp &
   firefox &
   vlc &
   ```

### Original Interface

1. **Load guide** in GUI text editor
2. **Click** "▶ Start Installation"
3. **Watch** in VNC window as apps install

---

## 🔧 Configuration

Create `.env` file:

```bash
# Required: Claude API key
CLAUDE_API_KEY=sk-ant-your-key-here

# Optional: File organizer watch folder
WATCH_FOLDER=/tmp/test_files
```

Get API key: https://console.anthropic.com/

---

## 🐳 Docker Commands

### Web Chatbot Interface
```bash
# Start
./run-chatbot.sh

# Stop
docker stop agent-chatbot

# Logs
docker logs -f agent-chatbot

# Access
http://localhost:8000        # Web interface
http://localhost:6080        # Direct noVNC access
```

### Original Interface
```bash
# Start
./run.sh

# Stop
docker stop desktop-agent-running

# Logs
docker logs -f desktop-agent-running

# VNC
vncviewer localhost:5901
```

---

## 📝 Example Workflow (Web Chatbot)

**In Browser (Chatbot):**
```
You: "Setup Python development environment"
Agent: [Analyzes request]
       [Updates apt packages]
       [Installs python3, pip, venv, git]
       [Verifies installations]
       ✅ Environment ready!
```

**In VNC Panel:**
```bash
# Test what was installed
python3 --version
pip3 --version
git --version
```

---

## 🔒 Security

Multiple security layers:
- ✅ **Command whitelist** - Only approved commands
- ✅ **Pattern blocking** - Blocks dangerous patterns (rm -rf /, etc.)
- ✅ **Docker isolation** - Contained environment
- ✅ **Input validation** - Sanitized command inputs
- ✅ **Comprehensive logging** - Full audit trail

See `utils/security.py` and `SECURITY.md` for details.

---

## 🚧 Requirements

- **Python** 3.10+
- **Claude API Key**
- **Docker** 20.10+ *(only for the Docker modes — not needed for `run-local.sh`)*
- **VNC Viewer** *(only for the original `run.sh` mode)*: `tigervnc-viewer` or `remmina`

**Install VNC viewer (optional, original interface only):**
```bash
sudo apt install tigervnc-viewer
```

---

## 🐧 WSL2 / Linux VM Notes

Running inside **WSL2** or a **headless Linux VM**? Use the local mode — no Docker required:

```bash
./run-local.sh        # chatbot only, no desktop environment
```

If you do want the full Docker + VNC experience on WSL2:

1. **Docker Desktop (recommended)** — enable the WSL2 backend in Docker Desktop settings on Windows.
   Ports are automatically forwarded, so `http://localhost:8000` works in the Windows browser.

2. **Docker Engine in WSL2** — install normally with `apt`; port forwarding usually works, but if
   `localhost` doesn't resolve add the WSL2 IP to your Windows hosts file or use:
   ```bash
   # Get your WSL2 IP
   ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
   # Then open http://<that-ip>:8000 in Windows browser
   ```

3. **The VNC desktop panel** (`run-chatbot.sh`) renders inside the browser via noVNC — no separate
   VNC client is needed. The panel connects to `http://localhost:6080` as seen from the browser
   (your Windows machine), which works automatically when using Docker Desktop.

4. **`run.sh` (original mode)** auto-launches `vncviewer` — this will fail on WSL2/headless
   systems since there is no local display server. Install a Windows VNC client instead and
   connect to `localhost:5901` from Windows, or use `run-chatbot.sh` which uses browser-based VNC.

---

## 📚 Documentation

- `CLAUDE.md` - Instructions for Claude Code
- `SECURITY.md` - Security architecture
- `TODO.md` - Development roadmap
- `desktop_agent_complete_architecture.md` - Technical details

---

## 🤝 Contributing

This is an AI-assisted development project. Key components:

1. **Agent**: LangChain-based autonomous agent with tool calling
2. **Tools**: Shell execution, package management, system info
3. **Interface**: Web-based chatbot + embedded VNC viewer
4. **Safety**: Command validation, Docker isolation

---

## 📄 License

See `LICENSE` file.

---

## 🎉 Features Comparison

| Feature | Web Chatbot | Original GUI |
|---------|-------------|--------------|
| UI | Web browser | VNC desktop |
| Chatbot | LangChain agent | Guide parser |
| Viewing | In-browser | Separate VNC client |
| Control | Natural language | Text guides |
| Best for | Interactive use | Batch installations |

---

**Built with Claude Sonnet-4 + LangChain + Docker**

*Modern AI-powered desktop automation*
