from fastmcp import FastMCP
import logging
import os
from dotenv import load_dotenv
from mcp_server.tools import account_info, balance, stock_prices, commodity_prices

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Reduce noise from external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)

# Initialize FastMCP server
mcp = FastMCP("Banking Agent Tools")

# Register all banking tools
account_info.register(mcp)
balance.register(mcp)
stock_prices.register(mcp)
commodity_prices.register(mcp)

if __name__ == "__main__":
    logger.info("Starting Banking Agent MCP Server...")
    logger.info("Available tools:")
    logger.info("  - Account Information (get_account_info, get_account_types)")
    logger.info("  - Balance Checking (check_balance, get_recent_transactions, get_total_portfolio_value)")
    logger.info("  - Stock Prices (get_stock_price, get_multiple_stock_prices)")
    logger.info("  - Commodity Prices (get_gold_price, get_silver_price, get_precious_metals_prices)")
    mcp.run(transport="sse", port=8001)
