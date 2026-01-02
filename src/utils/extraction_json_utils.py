import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class PortfolioField:
    investor: Optional[str] = None
    account: Optional[str] = None
    period_ending_dt: Optional[str] = None
    transaction_date: Optional[str] = None


def are_investor_account_names_unique(extraction_json: str) -> bool:
    seen = set()
    doc = json.loads(extraction_json)

    for entity in doc[0].get("entities", []):
        for portfolio in entity.get("portfolio", []):
            investor = portfolio.get("Investor", {}).get("Value")
            account = portfolio.get("Account", {}).get("Value")

            key = f"{(investor or '').strip()} | {(account or '').strip()}"
            if key in seen:
                return False
            seen.add(key)

    return True


def extract_portfolio_fields(extraction_json: str) -> PortfolioField:
    doc = json.loads(extraction_json)
    portfolio = doc[0]["entities"][0]["portfolio"][0]

    field = PortfolioField()

    if "Investor" in portfolio:
        field.investor = portfolio["Investor"].get("Value")

    if "Account" in portfolio:
        field.account = portfolio["Account"].get("Value")

    if "PeriodEndingDT" in portfolio:
        field.period_ending_dt = portfolio["PeriodEndingDT"].get("Value")
    elif "TransactionDate" in portfolio:
        field.transaction_date = portfolio["TransactionDate"].get("Value")

    return field
