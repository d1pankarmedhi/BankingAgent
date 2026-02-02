"""
Commodity Prices Tool
Fetches real-time gold and silver prices.
"""

import logging
import yfinance as yf
from datetime import datetime

logger = logging.getLogger("mcp_server")


def register(mcp):
    """Register commodity price tools with the MCP server"""
    
    @mcp.tool()
    def get_gold_price() -> str:
        """
        Get current gold spot price.
        
        Returns:
            Current gold price information
        """
        logger.info("Tool used: get_gold_price")
        
        try:
            # Using GC=F (Gold Futures) as proxy for spot price
            ticker = yf.Ticker("GC=F")
            info = ticker.info
            
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            if not current_price:
                return "Unable to fetch gold price at this time."
            
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            result = f"**Gold Spot Price**\n\n"
            result += f"- Current Price: ${current_price:,.2f} per troy ounce\n"
            result += f"- Previous Close: ${previous_close:,.2f}\n"
            result += f"- Change: ${change:+.2f} ({change_percent:+.2f}%)\n"
            result += f"\n*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
            return f"Error fetching gold price: {str(e)}"
    
    @mcp.tool()
    def get_silver_price() -> str:
        """
        Get current silver spot price.
        
        Returns:
            Current silver price information
        """
        logger.info("Tool used: get_silver_price")
        
        try:
            # Using SI=F (Silver Futures) as proxy for spot price
            ticker = yf.Ticker("SI=F")
            info = ticker.info
            
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            if not current_price:
                return "Unable to fetch silver price at this time."
            
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            result = f"**Silver Spot Price**\n\n"
            result += f"- Current Price: ${current_price:,.2f} per troy ounce\n"
            result += f"- Previous Close: ${previous_close:,.2f}\n"
            result += f"- Change: ${change:+.2f} ({change_percent:+.2f}%)\n"
            result += f"\n*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching silver price: {e}")
            return f"Error fetching silver price: {str(e)}"
    
    @mcp.tool()
    def get_precious_metals_prices() -> str:
        """
        Get current prices for both gold and silver.
        
        Returns:
            Current precious metals prices
        """
        logger.info("Tool used: get_precious_metals_prices")
        
        result = f"**Precious Metals Prices**\n\n"
        
        # Fetch gold
        try:
            gold_ticker = yf.Ticker("GC=F")
            gold_info = gold_ticker.info
            gold_price = gold_info.get('regularMarketPrice') or gold_info.get('currentPrice')
            gold_prev = gold_info.get('previousClose', 0)
            gold_change = gold_price - gold_prev if gold_price and gold_prev else 0
            gold_pct = (gold_change / gold_prev * 100) if gold_prev else 0
            
            if gold_price:
                result += f"### Gold (per troy oz)\n"
                result += f"- Price: ${gold_price:,.2f}\n"
                result += f"- Change: ${gold_change:+.2f} ({gold_pct:+.2f}%)\n\n"
            else:
                result += f"### Gold\n- Unable to fetch price\n\n"
        except Exception as e:
            logger.error(f"Error fetching gold: {e}")
            result += f"### Gold\n- Error: {str(e)}\n\n"
        
        # Fetch silver
        try:
            silver_ticker = yf.Ticker("SI=F")
            silver_info = silver_ticker.info
            silver_price = silver_info.get('regularMarketPrice') or silver_info.get('currentPrice')
            silver_prev = silver_info.get('previousClose', 0)
            silver_change = silver_price - silver_prev if silver_price and silver_prev else 0
            silver_pct = (silver_change / silver_prev * 100) if silver_prev else 0
            
            if silver_price:
                result += f"### Silver (per troy oz)\n"
                result += f"- Price: ${silver_price:,.2f}\n"
                result += f"- Change: ${silver_change:+.2f} ({silver_pct:+.2f}%)\n\n"
            else:
                result += f"### Silver\n- Unable to fetch price\n\n"
        except Exception as e:
            logger.error(f"Error fetching silver: {e}")
            result += f"### Silver\n- Error: {str(e)}\n\n"
        
        result += f"*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        return result
