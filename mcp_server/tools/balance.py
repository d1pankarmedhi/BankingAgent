import logging
from mcp_server.data import (
    get_accounts_by_customer,
    get_account_by_id,
    get_transactions_by_customer,
    get_total_balance
)

logger = logging.getLogger("mcp_server")


def register(mcp):
    """Register balance checking tools with the MCP server"""
    
    @mcp.tool()
    def check_balance(customer_id: str, account_type: str = "all") -> str:
        """
        Check account balance for a customer.
        
        Args:
            customer_id: The customer ID (e.g., C001)
            account_type: Type of account (checking, savings, investment, or all)
            
        Returns:
            Account balance information
        """
        logger.info(f"Tool used: check_balance (Customer: {customer_id}, Type: {account_type})")
        
        accounts = get_accounts_by_customer(customer_id)
        if not accounts:
            return f"No accounts found for customer {customer_id}."
        
        if account_type.lower() == "all":
            result = f"**Balance Summary for Customer {customer_id}**\n\n"
            total = 0
            for acc in accounts:
                result += f"- {acc['account_type'].title()}: ${acc['balance']:,.2f}\n"
                total += acc['balance']
            result += f"\n**Total Balance: ${total:,.2f} USD**"
            return result
        else:
            # Find specific account type
            matching_accounts = [acc for acc in accounts if acc['account_type'].lower() == account_type.lower()]
            if not matching_accounts:
                return f"No {account_type} account found for customer {customer_id}."
            
            acc = matching_accounts[0]
            result = f"**{acc['account_type'].title()} Account Balance**\n"
            result += f"- Account Number: {acc['account_number']}\n"
            result += f"- Balance: ${acc['balance']:,.2f} {acc['currency']}\n"
            result += f"- Status: {acc['status']}"
            return result
    
    @mcp.tool()
    def get_recent_transactions(customer_id: str, limit: int = 5) -> str:
        """
        Get recent transactions for a customer.
        
        Args:
            customer_id: The customer ID (e.g., C001)
            limit: Number of recent transactions to retrieve (default: 5)
            
        Returns:
            Recent transaction history
        """
        logger.info(f"Tool used: get_recent_transactions (Customer: {customer_id}, Limit: {limit})")
        
        transactions = get_transactions_by_customer(customer_id, limit)
        if not transactions:
            return f"No recent transactions found for customer {customer_id}."
        
        result = f"**Recent Transactions for Customer {customer_id}**\n\n"
        for txn in transactions:
            sign = "+" if txn['type'] == 'credit' else "-"
            result += f"### {txn['date']}\n"
            result += f"- Description: {txn['description']}\n"
            result += f"- Amount: {sign}${abs(txn['amount']):,.2f}\n"
            result += f"- Balance After: ${txn['balance_after']:,.2f}\n\n"
        
        return result
    
    @mcp.tool()
    def get_total_portfolio_value(customer_id: str) -> str:
        """
        Get total portfolio value across all accounts for a customer.
        
        Args:
            customer_id: The customer ID (e.g., C001)
            
        Returns:
            Total portfolio value
        """
        logger.info(f"Tool used: get_total_portfolio_value (Customer: {customer_id})")
        
        total = get_total_balance(customer_id)
        if total == 0:
            return f"No accounts found for customer {customer_id}."
        
        accounts = get_accounts_by_customer(customer_id)
        result = f"**Total Portfolio Value for Customer {customer_id}**\n\n"
        result += f"Total Value: ${total:,.2f} USD\n"
        result += f"Accounts: {len(accounts)}\n"
        return result
