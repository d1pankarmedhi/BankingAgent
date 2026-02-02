import logging
from mcp_server.data import (
    get_customer_by_id,
    get_accounts_by_customer,
    get_account_by_id
)

logger = logging.getLogger("mcp_server")


def register(mcp):
    """Register account information tools with the MCP server"""
    
    @mcp.tool()
    def get_account_info(customer_id: str) -> str:
        """
        Get comprehensive account information for a customer.
        
        Args:
            customer_id: The customer ID (e.g., C001)
            
        Returns:
            Formatted account information including all accounts
        """
        logger.info(f"Tool used: get_account_info (Customer: {customer_id})")
        
        customer = get_customer_by_id(customer_id)
        if not customer:
            return f"Error: Customer {customer_id} not found."
        
        accounts = get_accounts_by_customer(customer_id)
        if not accounts:
            return f"No accounts found for customer {customer_id}."
        
        # Format customer info
        result = f"**Customer Information**\n"
        result += f"- Name: {customer['name']}\n"
        result += f"- Customer ID: {customer['customer_id']}\n"
        result += f"- Email: {customer['email']}\n"
        result += f"- Phone: {customer['phone']}\n"
        result += f"- Status: {customer['status']}\n"
        result += f"- Member Since: {customer['joined_date']}\n\n"
        
        # Format accounts
        result += f"**Accounts ({len(accounts)})**\n\n"
        for acc in accounts:
            result += f"### {acc['account_type'].title()} Account\n"
            result += f"- Account Number: {acc['account_number']}\n"
            result += f"- Balance: ${acc['balance']:,.2f} {acc['currency']}\n"
            result += f"- Status: {acc['status']}\n"
            result += f"- Opening Date: {acc['opening_date']}\n"
            result += f"- Interest Rate: {acc['interest_rate']}%\n\n"
        
        return result
    
    @mcp.tool()
    def get_account_types(customer_id: str) -> str:
        """
        Get a list of account types for a customer.
        
        Args:
            customer_id: The customer ID (e.g., C001)
            
        Returns:
            List of account types
        """
        logger.info(f"Tool used: get_account_types (Customer: {customer_id})")
        
        accounts = get_accounts_by_customer(customer_id)
        if not accounts:
            return f"No accounts found for customer {customer_id}."
        
        account_types = [acc['account_type'].title() for acc in accounts]
        return f"Account types for {customer_id}: {', '.join(account_types)}"
