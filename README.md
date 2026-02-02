# Banking Agent

A banking agent system built with MCP (Model Context Protocol) server architecture and LangGraph, featuring multi-LLM support.

## Features

✅ **Account Management**
- Comprehensive account information
- Multiple account types (checking, savings, investment)
- Account status and metadata

✅ **Balance Operations**
- Check balances by account type
- Total portfolio value calculation
- Recent transaction history

✅ **Market Data**
- Real-time stock prices
- Multiple stock symbols support
- Gold and silver commodity prices

✅ **Multi-LLM Support**
- Azure OpenAI
- Google Gemini
- Ollama (local models)
- OpenAI


## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd AIAgent
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env .env.local
   # Edit .env.local with your API keys
   ```

## Configuration

### LLM Provider Selection

Set the `LLM_PROVIDER` environment variable to one of:
- `azure_openai` (default)
- `gemini`
- `ollama`
- `openai`

### Provider-Specific Configuration

**Azure OpenAI:**
```bash
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

**Google Gemini:**
```bash
GOOGLE_API_KEY=your_key
GEMINI_MODEL=gemini-pro
```

**Ollama (Local):**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**OpenAI:**
```bash
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4
```

## Running the System

### Using the Management Script (Recommended)

The `manage.sh` script provides easy management of all services:

```bash
# Start all services (MCP, Agent, and UI)
./manage.sh start

# Check status
./manage.sh status

# View logs
./manage.sh logs all

# Stop all services
./manage.sh stop
```

**Available Commands:**
- `start [mcp|agent|ui|all]` - Start services
- `stop [mcp|agent|ui|all]` - Stop services
- `restart [mcp|agent|ui|all]` - Restart services
- `status` - Show status of all services
- `logs [mcp|agent|ui|all] [lines]` - Show logs
- `clean` - Clean log and PID files
- `help` - Show detailed help

### Manual Setup (Alternative)

#### 1. Start MCP Server

```bash
uv run python -m mcp_server.main
```

The server will start on port 8001 and register all banking tools.

#### 2. Start Agent Service

In a separate terminal:

```bash
uv run python -m mcp_client.agent_service
```

The FastAPI service will start on port 8000.

#### 3. Start Chat UI

In a third terminal:

```bash
cd frontend
npm run dev
```

This opens the light-themed web interface to chat with the agent.

## Example Queries

Try these queries in the test interface:

- "What's my checking account balance?"
- "Show me my account information"
- "What's the current price of AAPL stock?"
- "What are the current gold and silver prices?"
- "Show me my recent transactions"
- "What's my total portfolio value?"
- "Check the price of MSFT, GOOGL, and TSLA stocks"

## Available Tools

### Account Information
- `get_account_info` - Get comprehensive account details
- `get_account_types` - List account types for a customer

### Balance Checking
- `check_balance` - Check balance for specific account type or all accounts
- `get_recent_transactions` - View recent transaction history
- `get_total_portfolio_value` - Calculate total value across all accounts

### Stock Prices
- `get_stock_price` - Get price for a single stock
- `get_multiple_stock_prices` - Get prices for multiple stocks

### Commodity Prices
- `get_gold_price` - Current gold spot price
- `get_silver_price` - Current silver spot price
- `get_precious_metals_prices` - Both gold and silver prices

## Development

### Project Structure

- `mcp_server/` - All MCP server code
  - `main.py` - Server entry point
  - `data.py` - Mock database
  - `tools/` - Tool implementations

- `mcp_client/` - All client/agent code
  - `agent_service.py` - LangGraph agent with FastAPI
  - `llm_config.py` - Multi-LLM configuration

### Adding New Tools

1. Create a new tool file in `mcp_server/tools/`
2. Implement the `register(mcp)` function
3. Register the tool in `mcp_server/main.py`

### Switching LLM Providers

Simply change the `LLM_PROVIDER` environment variable and provide the required credentials. No code changes needed!

## Customer Data

The system includes mock data for three customers:
- `C001` - John Doe (default)
- `C002` - Jane Smith
- `C003` - Bob Johnson

Switch customers in the UI or update the `customer_id` in `frontend/src/App.jsx`.

## Troubleshooting

**MCP Server Connection Error:**
- Ensure the MCP server is running on port 8001
- Check firewall settings

**LLM Provider Errors:**
- Verify API keys are correct
- Check rate limits for your provider
- Ensure the provider supports tool calling

**Stock/Commodity Price Errors:**
- Prices are fetched from Yahoo Finance
- Requires internet connection
- Some symbols may not be available

## License

MIT License
