import datetime
import pandas as pd
import numpy as np

# Tax bracket data
TAX_BRACKETS = {
    "United States": [
        (0, 11000, 0.10),
        (11001, 44725, 0.12),
        (44726, 95375, 0.22),
        (95376, 182100, 0.24),
        (182101, 231250, 0.32),
        (231251, 578125, 0.35),
        (578126, float('inf'), 0.37)
    ]
}

# Common deductions for freelancers
COMMON_DEDUCTIONS = {
    "Home Office": {"description": "Portion of home used for business", "type": "percentage"},
    "Internet & Phone": {"description": "Business portion of utilities", "type": "percentage"},
    "Software & Subscriptions": {"description": "Business software and tools", "type": "fixed"},
    "Office Supplies": {"description": "Physical supplies and equipment", "type": "fixed"},
    "Professional Development": {"description": "Courses and training", "type": "fixed"},
    "Travel": {"description": "Business-related travel", "type": "fixed"},
    "Health Insurance": {"description": "Self-employed health insurance", "type": "fixed"},
    "Retirement Contributions": {"description": "SEP IRA, Solo 401(k)", "type": "fixed"},
    "Professional Services": {"description": "Legal and accounting fees", "type": "fixed"},
    "Marketing & Advertising": {"description": "Promotion and advertising costs", "type": "fixed"}
}

# Retirement account limits (2024)
RETIREMENT_LIMITS = {
    "Traditional IRA": 7000,
    "Roth IRA": 7000,
    "SEP IRA": 69000,
    "Solo 401(k)": 69000
}

def calculate_tax(income: float, brackets: list) -> float:
    """
    Calculate tax based on income and tax brackets
    """
    tax = 0
    for lower, upper, rate in brackets:
        if income > lower:
            taxable_amount = min(income - lower, upper - lower)
            tax += taxable_amount * rate
    return tax

def calculate_quarterly_tax(annual_income: float, tax_amount: float) -> dict:
    """
    Calculate quarterly tax payments and due dates
    """
    quarterly_amount = tax_amount / 4
    current_year = datetime.datetime.now().year
    
    quarters = {
        "Q1": {"due_date": f"April 15, {current_year}", "amount": quarterly_amount},
        "Q2": {"due_date": f"June 15, {current_year}", "amount": quarterly_amount},
        "Q3": {"due_date": f"September 15, {current_year}", "amount": quarterly_amount},
        "Q4": {"due_date": f"January 15, {current_year + 1}", "amount": quarterly_amount}
    }
    return quarters

def get_tax_optimization_tips(income: float, expenses: dict, deductions: dict) -> list:
    """
    Generate personalized tax optimization tips
    """
    tips = []
    
    # Retirement contribution tips
    if "Retirement Contributions" not in deductions:
        tips.append("Consider contributing to a retirement account (SEP IRA or Solo 401(k)) to reduce taxable income")
    
    # Home office deduction tip
    if "Home Office" not in deductions:
        tips.append("If you work from home, you may be eligible for the home office deduction")
    
    # Health insurance tip
    if "Health Insurance" not in deductions:
        tips.append("Self-employed individuals can deduct health insurance premiums")
    
    # High income tips
    if income > 100000:
        tips.append("Consider forming an S-Corporation to potentially reduce self-employment tax")
        
    return tips

def calculate_monthly_goal(annual_goal: float, tax_rate: float) -> dict:
    """
    Calculate monthly income needed to reach annual goal after taxes
    """
    monthly_before_tax = annual_goal / 12
    tax_amount = monthly_before_tax * tax_rate
    monthly_after_tax = monthly_before_tax - tax_amount
    
    return {
        "monthly_before_tax": monthly_before_tax,
        "monthly_after_tax": monthly_after_tax,
        "tax_amount": tax_amount
    }

def calculate_retirement_impact(amount: float, years: int, rate: float = 0.07) -> dict:
    """
    Calculate the impact of retirement savings over time
    """
    future_value = amount * ((1 + rate) ** years)
    tax_savings = amount * 0.22  # Assuming 22% tax bracket
    
    return {
        "future_value": future_value,
        "tax_savings": tax_savings,
        "total_contribution": amount * years
    }

def adjust_for_inflation(amount: float, years: int, inflation_rate: float = 0.03) -> float:
    """
    Adjust amount for inflation over specified years
    """
    return amount * ((1 + inflation_rate) ** years)

# Currency conversion rates (to be updated with real API in production)
CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.35,
    "AUD": 1.52
}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert amount between currencies
    """
    # Convert to USD first
    usd_amount = amount / CURRENCY_RATES[from_currency]
    # Convert from USD to target currency
    return usd_amount * CURRENCY_RATES[to_currency] 