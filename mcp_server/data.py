from datetime import datetime, timedelta
from typing import Dict, List, Any

# Mock customer database
CUSTOMERS = {
    "C001": {
        "customer_id": "C001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0101",
        "status": "active",
        "joined_date": "2020-01-15"
    },
    "C002": {
        "customer_id": "C002",
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-0102",
        "status": "active",
        "joined_date": "2019-06-20"
    },
    "C003": {
        "customer_id": "C003",
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "phone": "+1-555-0103",
        "status": "active",
        "joined_date": "2021-03-10"
    }
}

# Mock accounts database
ACCOUNTS = {
    "A001": {
        "account_id": "A001",
        "customer_id": "C001",
        "account_type": "checking",
        "account_number": "****1234",
        "balance": 5420.50,
        "currency": "USD",
        "status": "active",
        "opening_date": "2020-01-15",
        "interest_rate": 0.5
    },
    "A002": {
        "account_id": "A002",
        "customer_id": "C001",
        "account_type": "savings",
        "account_number": "****5678",
        "balance": 15750.00,
        "currency": "USD",
        "status": "active",
        "opening_date": "2020-02-20",
        "interest_rate": 2.5
    },
    "A003": {
        "account_id": "A003",
        "customer_id": "C001",
        "account_type": "investment",
        "account_number": "****9012",
        "balance": 47890.25,
        "currency": "USD",
        "status": "active",
        "opening_date": "2021-05-10",
        "interest_rate": 0.0
    },
    "A004": {
        "account_id": "A004",
        "customer_id": "C002",
        "account_type": "checking",
        "account_number": "****3456",
        "balance": 3280.75,
        "currency": "USD",
        "status": "active",
        "opening_date": "2019-06-20",
        "interest_rate": 0.5
    },
    "A005": {
        "account_id": "A005",
        "customer_id": "C002",
        "account_type": "savings",
        "account_number": "****7890",
        "balance": 22500.00,
        "currency": "USD",
        "status": "active",
        "opening_date": "2019-07-01",
        "interest_rate": 2.5
    },
    "A006": {
        "account_id": "A006",
        "customer_id": "C003",
        "account_type": "checking",
        "account_number": "****2468",
        "balance": 1875.30,
        "currency": "USD",
        "status": "active",
        "opening_date": "2021-03-10",
        "interest_rate": 0.5
    }
}

# Mock recent transactions
TRANSACTIONS = {
    "C001": [
        {
            "transaction_id": "T001",
            "account_id": "A001",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "description": "Grocery Store",
            "amount": -85.50,
            "type": "debit",
            "balance_after": 5420.50
        },
        {
            "transaction_id": "T002",
            "account_id": "A001",
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "description": "Salary Deposit",
            "amount": 3500.00,
            "type": "credit",
            "balance_after": 5506.00
        },
        {
            "transaction_id": "T003",
            "account_id": "A002",
            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "description": "Interest Credit",
            "amount": 32.85,
            "type": "credit",
            "balance_after": 15750.00
        },
        {
            "transaction_id": "T004",
            "account_id": "A003",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "description": "Stock Purchase - AAPL",
            "amount": -2500.00,
            "type": "debit",
            "balance_after": 47890.25
        }
    ],
    "C002": [
        {
            "transaction_id": "T005",
            "account_id": "A004",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "description": "Electric Bill",
            "amount": -125.50,
            "type": "debit",
            "balance_after": 3280.75
        },
        {
            "transaction_id": "T006",
            "account_id": "A004",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "description": "ATM Withdrawal",
            "amount": -200.00,
            "type": "debit",
            "balance_after": 3406.25
        }
    ],
    "C003": [
        {
            "transaction_id": "T007",
            "account_id": "A006",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "description": "Restaurant",
            "amount": -45.80,
            "type": "debit",
            "balance_after": 1875.30
        }
    ]
}


def get_customer_by_id(customer_id: str) -> Dict[str, Any] | None:
    """Get customer information by ID"""
    return CUSTOMERS.get(customer_id)


def get_accounts_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    """Get all accounts for a customer"""
    return [acc for acc in ACCOUNTS.values() if acc["customer_id"] == customer_id]


def get_account_by_id(account_id: str) -> Dict[str, Any] | None:
    """Get account by account ID"""
    return ACCOUNTS.get(account_id)


def get_transactions_by_customer(customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent transactions for a customer"""
    transactions = TRANSACTIONS.get(customer_id, [])
    return transactions[:limit]


def get_total_balance(customer_id: str) -> float:
    """Calculate total balance across all accounts for a customer"""
    accounts = get_accounts_by_customer(customer_id)
    return sum(acc["balance"] for acc in accounts)
