# 🏦 Banking Agent

A banking agent system built with **Model Context Protocol (MCP)** server architecture and **LangGraph**, featuring multi-LLM support.

---

## 🌟 Features

- ✅ **Account Management**: Comprehensive account information across types (Checking, Savings, Investment).
- ✅ **Balance Operations**: Check balances, calculate total portfolio value, and view transaction history.
- ✅ **Market Data**: Real-time stock prices and commodity tracking (Gold, Silver) via Yahoo Finance.
- ✅ **Multi-LLM Support**: Native integration with Azure OpenAI, Gemini, Ollama (local), and OpenAI.

---

## ⚙️ Installation

1. **Clone and navigate to the project:**
   ```bash
   cd AIAgent
   ```

2. **Install dependencies using [uv](https://github.com/astral-sh/uv):**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env .env.local
   # Edit .env.local with your API keys and provider settings
   ```

---

## 🛠️ Configuration

### LLM Provider Selection
Set the `LLM_PROVIDER` environment variable to one of: `azure_openai`, `gemini`, `ollama`, or `openai`.

### Provider-Specific Settings
- **Azure OpenAI**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`
- **Google Gemini**: `GOOGLE_API_KEY`, `GEMINI_MODEL`
- **Ollama**: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- **OpenAI**: `OPENAI_API_KEY`, `OPENAI_MODEL`

---

## 🚀 Running the System

### ⚡ Using the Management Script (Recommended)
The `manage.sh` script handles service orchestration and uses process groups for robust termination.

```bash
# Start all services (MCP, Agent, and UI)
./manage.sh start

# Check status of all running components
./manage.sh status

# Stop all services and their child processes
./manage.sh stop
```

**Common Commands:**
- `start [mcp|agent|ui|all]`
- `stop [mcp|agent|ui|all]`
- `restart [mcp|agent|ui|all]`
- `logs [mcp|agent|ui|all] [lines]`
- `clean` (removes logs and PID files)

### 🧩 Manual Setup (Alternative)
Run these in separate terminals:
1. **MCP Server**: `uv run python -m mcp_server.main` (Port 8001)
2. **Agent Service**: `uv run python -m mcp_client.agent_service` (Port 8000)
3. **Frontend**: `cd frontend && npm run dev` (Port 5173)

---

## 🛠️ Development

- **Adding Tools**: Create a new tool in `mcp_server/tools/`, implement `register(mcp)`, and add to `mcp_server/main.py`.
- **Switching LLMs**: No code changes needed—simply update `LLM_PROVIDER` in your `.env`.

---

## 🔧 Troubleshooting

- **MCP Connection Error**: Ensure the server is on port `8001`.
- **LLM Errors**: Verify provider keys and ensure your model supports tool calling.
- **Orphan Processes**: `manage.sh stop` now uses **process groups** to ensure Vite and other subprocesses are killed correctly. If manual processes persist, use `pkill -f vite`.

---

## 📄 License
MIT License
