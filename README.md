# 🤖 Desktop Agent

# Video 
https://youtu.be/uwGJwdlxXp4

**AI-Powered Installation Assistant for Linux**

An intelligent desktop assistant that automates software installation using Claude AI. Choose between a modern web interface or the original VNC desktop environment.

---

## 🚀 Quick Start

### **Option 1: Web Chatbot Interface (Recommended)**

Modern web interface with AI chatbot + VNC desktop side-by-side:

```bash
# 1. Set your Claude API key
echo 'CLAUDE_API_KEY=your_key_here' > .env

# 2. Run the chatbot
./run-chatbot.sh

# 3. Open browser
# http://localhost:8000
```

**What you get:**
- **Left panel**: AI chatbot to install apps
- **Right panel**: VNC desktop to launch and test apps
- **All in one browser window!**

### **Option 2: Original VNC Desktop**

Classic desktop environment with tkinter GUI:

```bash
# 1. Set your Claude API key
echo 'CLAUDE_API_KEY=your_key_here' > .env

# 2. Run the original interface
./run.sh

# VNC viewer will auto-connect
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
├── chatbot.py                # ⭐ Web chatbot interface
├── Dockerfile.chatbot        # ⭐ Web chatbot Docker config
├── run-chatbot.sh            # ⭐ Web chatbot launcher
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

- **Docker** 20.10+
- **Python** 3.10+
- **Claude API Key**
- **VNC Viewer** (for original interface): `tigervnc-viewer` or `remmina`

**Install VNC viewer (optional):**
```bash
sudo apt install tigervnc-viewer
```

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
