"""
SimpleFIN2Polars Quickstart Example

This script demonstrates basic usage of the simplefin2polars package.
"""

from simplefin2polars import (
    sfin_claim_token,
    sfin_set_access_url,
    sfin_get_access_url,
    sfin_accounts,
    sfin_transactions,
)
from datetime import date, timedelta
import polars as pl


def first_time_setup():
    """
    One-time setup: Claim your token and store the Access URL.
    
    Run this function once to set up your credentials.
    """
    print("=== First Time Setup ===")
    print("\nStep 1: Get a token from https://bridge.simplefin.org/simplefin/create")
    
    token = input("\nPaste your SimpleFIN token here: ")
    
    print("\nStep 2: Claiming token and exchanging for Access URL...")
    access_url = sfin_claim_token(token)
    
    print("\nStep 3: Storing Access URL in keyring...")
    sfin_set_access_url(access_url, key="personal")
    
    print("\n✓ Setup complete! You can now query your accounts.")


def get_account_balances():
    """
    Retrieve current account balances.
    """
    print("\n=== Account Balances ===")
    
    result = sfin_accounts(key="personal", balances_only=True)
    
    # Display accounts
    accounts_df = result["accounts"]
    print(accounts_df.select(["account_name", "balance", "currency", "balance_date"]))
    
    # Check for any errors
    if len(result["errors"]) > 0:
        print("\n⚠ Errors encountered:")
        print(result["errors"])


def analyze_recent_spending():
    """
    Analyze spending over the last 30 days.
    """
    print("\n=== Spending Analysis (Last 30 Days) ===")
    
    # Get transactions from the last 30 days
    start = date.today() - timedelta(days=30)
    
    result = sfin_accounts(key="personal", start_date=start)
    
    txns = result["transactions"]
    accounts = result["accounts"]
    
    # Join transactions with account names
    analysis = (
        txns
        .filter(pl.col("amount") < 0)  # Only debits (spending)
        .join(
            accounts.select(["account_id", "account_name"]),
            on="account_id",
            how="left"
        )
        .group_by("account_name")
        .agg([
            pl.col("amount").sum().alias("total_spent"),
            pl.col("amount").count().alias("transaction_count")
        ])
        .sort("total_spent")
    )
    
    print(analysis)


def get_recent_transactions():
    """
    Get recent transactions with account details.
    """
    print("\n=== Recent Transactions (Last 7 Days) ===")
    
    start = date.today() - timedelta(days=7)
    
    # Use the convenience function that returns transactions directly
    txns = sfin_transactions(
        key="personal",
        start_date=start,
        join_accounts=True  # Automatically joins account metadata
    )
    
    # Display recent transactions
    recent = (
        txns
        .select([
            "posted",
            "account_name",
            "description",
            "amount",
            "pending"
        ])
        .sort("posted", descending=True)
        .head(10)
    )
    
    print(recent)


def main():
    """
    Main function - demonstrates typical usage workflow.
    """
    print("SimpleFIN2Polars Quickstart")
    print("=" * 50)
    
    # Check if we have credentials stored
    try:
        access_url = sfin_get_access_url(key="personal")
        print("✓ Found stored credentials")
    except Exception:
        print("✗ No stored credentials found")
        print("\nRunning first-time setup...")
        first_time_setup()
        return
    
    # Run examples
    try:
        get_account_balances()
        analyze_recent_spending()
        get_recent_transactions()
        
        print("\n" + "=" * 50)
        print("✓ Quickstart complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nIf this is your first time, run first_time_setup() first.")


if __name__ == "__main__":
    main()
