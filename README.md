# JARVIS - Multimodal Agentic AI Assistant

<div align="center">

![JARVIS](https://img.shields.io/badge/JARVIS-AI%20Assistant-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![LLaMA](https://img.shields.io/badge/LLaMA-3.1%208B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Asisten AI multimodal berbasis agentic architecture dengan LLaMA 3.1 8B**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## 📋 Overview

JARVIS adalah asisten AI multimodal berbasis agentic architecture yang dibangun menggunakan Large Language Model lokal melalui Ollama dengan model LLaMA 3.1 8B. Sistem ini mampu berinteraksi melalui teks dan suara, melakukan reasoning dan perencanaan tugas, serta mengeksekusi aksi nyata melalui tool calling manual dan Model Context Protocol (MCP).

### 🎯 Key Features

- **🤖 Agentic Reasoning**: Plan-Act-Observe loop untuk task execution
- **🗣️ Multimodal**: Input/output teks dan suara
- **🔧 Tool Calling**: Manual JSON-based tool execution
- **🔌 MCP Integration**: Modular external system integration
- **💾 Memory System**: Short-term, long-term, dan semantic memory (RAG)
- **🌐 Multi-channel**: Web UI, Telegram, Voice interface
- **🔒 Privacy-First**: Local LLM dan processing

## 🏗️ Architecture

```
User (Web UI / Voice / Telegram)
    ↓
Input Normalization
    ↓
LLaMA 3.1 8B (Ollama)
    ↓
Agent Core (Plan-Act-Observe)
    ↓
Tool Router (MCP Client)
    ↓
MCP Servers (Calendar, Gmail, OS, DB, Telegram)
    ↓
Observation & Response
```

### Core Components

- **Agent Core**: Implementasi agentic loop dengan planning, execution, dan observation
- **LLM Integration**: Ollama client untuk LLaMA 3.1 8B
- **MCP Client**: Komunikasi dengan MCP servers
- **Memory System**: Three-tier memory architecture
- **API Layer**: REST dan WebSocket endpoints

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- [Ollama](https://ollama.ai/) installed and running
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jarvis
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Pull Ollama models**
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

4. **Configure environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   cd backend
   python -c "from app.models.database import init_db; init_db()"
   ```

## 💻 Usage

### Starting the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:
```bash
cd backend
python -m app.main
```

### API Endpoints

- **Health Check**: `GET /health`
- **Chat**: `POST /api/chat/send`
- **WebSocket**: `WS /api/ws/chat`
- **Voice STT**: `POST /api/voice/stt`
- **Voice TTS**: `POST /api/voice/tts`

### Example Chat Request

```bash
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my schedule today?",
    "conversation_id": "optional-uuid"
  }'
```

### WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Hello JARVIS!',
    conversation_id: 'uuid'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data);
};
```

## 📚 Documentation

### Project Structure

```
jarvis/
├── backend/
│   ├── app/
│   │   ├── agent/          # Agentic reasoning
│   │   ├── api/            # REST & WebSocket endpoints
│   │   ├── llm/            # Ollama integration
│   │   ├── mcp/            # MCP client
│   │   ├── models/         # Database models
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app
│   ├── .env.example        # Environment template
│   └── requirements.txt    # Dependencies
├── mcp-servers/            # MCP server implementations
├── frontend/               # Next.js web UI (coming soon)
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Agent Loop

JARVIS menggunakan **Plan-Act-Observe** loop:

1. **Plan**: LLM menganalisis request dan membuat execution plan
2. **Act**: Agent mengeksekusi tools yang diperlukan via MCP
3. **Observe**: LLM menganalisis hasil dan menentukan next action

### Available Tools

- **Memory**: save_conversation, get_user_preferences, log_interaction
- **Vector DB**: semantic_search, retrieve_context, store_embedding
- **Telegram**: send_message, get_updates, send_notification
- **Calendar**: list_events, create_event, update_event, delete_event
- **Gmail**: list_emails, read_email, create_draft, send_email
- **Windows OS**: open_application, run_powershell, manage_files
- **Voice**: transcribe_audio, synthesize_speech

## 🔧 Configuration

Edit `backend/.env` to configure:

- **Ollama**: URL, model, timeout
- **Database**: SQLite/PostgreSQL URL, ChromaDB path
- **External APIs**: Google Calendar, Gmail, Telegram tokens
- **MCP Servers**: URLs for each MCP server
- **API**: Host, port, CORS origins

## 🧪 Development

### Running Tests

```bash
pytest backend/tests/
```

### Code Style

```bash
# Format code
black backend/

# Lint
ruff backend/
```

## 📝 Roadmap

- [x] Phase 1: Core infrastructure & agent loop
- [ ] Phase 2: Memory system implementation
- [ ] Phase 3: MCP servers development
- [ ] Phase 4: Voice interface (STT/TTS)
- [ ] Phase 5: Web frontend (Next.js)
- [ ] Phase 6: External integrations
- [ ] Phase 7: Testing & documentation
- [ ] Phase 8: Deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [LLaMA](https://ai.meta.com/llama/) by Meta AI
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Model Context Protocol](https://modelcontextprotocol.io/) for tool integration

---

<div align="center">

**Built with ❤️ using LLaMA 3.1 8B and Ollama**

</div>
