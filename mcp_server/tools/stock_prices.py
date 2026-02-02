import logging
import yfinance as yf
from datetime import datetime

logger = logging.getLogger("mcp_server")


def register(mcp):
    """Register stock price tools with the MCP server"""
    
    @mcp.tool()
    def get_stock_price(symbol: str) -> str:
        """
        Get current stock price for a given symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
            
        Returns:
            Current stock price and information
        """
        logger.info(f"Tool used: get_stock_price (Symbol: {symbol})")
        
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                return f"Unable to fetch price for {symbol}. Please verify the symbol is correct."
            
            # Get additional info
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            company_name = info.get('longName', symbol)
            market_cap = info.get('marketCap')
            volume = info.get('volume')
            
            result = f"**{company_name} ({symbol.upper()})**\n\n"
            result += f"- Current Price: ${current_price:.2f}\n"
            result += f"- Previous Close: ${previous_close:.2f}\n"
            result += f"- Change: ${change:+.2f} ({change_percent:+.2f}%)\n"
            
            if market_cap:
                result += f"- Market Cap: ${market_cap:,.0f}\n"
            if volume:
                result += f"- Volume: {volume:,}\n"
            
            result += f"\n*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return f"Error fetching stock price for {symbol}: {str(e)}"
    
    @mcp.tool()
    def get_multiple_stock_prices(symbols: str) -> str:
        """
        Get current prices for multiple stocks.
        
        Args:
            symbols: Comma-separated stock ticker symbols (e.g., "AAPL,GOOGL,MSFT")
            
        Returns:
            Current stock prices for all symbols
        """
        logger.info(f"Tool used: get_multiple_stock_prices (Symbols: {symbols})")
        
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        result = f"**Stock Prices for {len(symbol_list)} Symbols**\n\n"
        
        for symbol in symbol_list:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                previous_close = info.get('previousClose', 0)
                change = current_price - previous_close if current_price and previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                if current_price:
                    result += f"### {symbol}\n"
                    result += f"- Price: ${current_price:.2f}\n"
                    result += f"- Change: ${change:+.2f} ({change_percent:+.2f}%)\n\n"
                else:
                    result += f"### {symbol}\n- Unable to fetch price\n\n"
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                result += f"### {symbol}\n- Error: {str(e)}\n\n"
        
        result += f"*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        return result
