import datetime
import pandas as pd
import numpy as np
import requests
from typing import Dict, Union
import streamlit as st

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
    Generate personalized tax optimization tips based on user's financial data
    """
    tips = []
    total_deductions = sum(deductions.values()) if deductions else 0
    expense_ratio = sum(expense["amount"] for expense in expenses) / income if income > 0 else 0
    
    # Retirement contribution tips
    if "Retirement Contributions" not in deductions:
        if income > 100000:
            tips.append("💰 High Income Tip: Maximize your retirement contributions with a SEP IRA or Solo 401(k) to reduce taxable income by up to $69,000")
        else:
            tips.append("💡 Consider contributing to a retirement account (Traditional IRA: $7,000 limit) to reduce taxable income")
    
    # Home office deduction tip
    if "Home Office" not in deductions:
        tips.append("🏠 If you work from home, you may be eligible for the home office deduction - typically 10-20% of home expenses")
    
    # Health insurance tip
    if "Health Insurance" not in deductions:
        tips.append("🏥 Self-employed individuals can deduct 100% of health insurance premiums for themselves and family")
    
    # Business expense tips
    if expense_ratio < 0.2:  # If expenses are less than 20% of income
        tips.append("📊 Your expense ratio seems low. Consider tracking all eligible business expenses including:")
        tips.append("   • Software subscriptions and tools")
        tips.append("   • Professional development and training")
        tips.append("   • Office supplies and equipment")
    
    # High income tips
    if income > 100000:
        tips.append("💼 Consider forming an S-Corporation to potentially reduce self-employment tax")
        if "Professional Services" not in deductions:
            tips.append("⚖️ At your income level, consulting with a tax professional could lead to significant savings")
    
    # Quarterly tax payment tips
    tips.append("📅 Remember to make quarterly estimated tax payments to avoid penalties")
    
    # Education and marketing tips
    if "Professional Development" not in deductions:
        tips.append("📚 Educational expenses related to maintaining or improving your skills are tax-deductible")
    
    if "Marketing & Advertising" not in deductions:
        tips.append("📣 Marketing and advertising costs are fully deductible business expenses")
    
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

# Cache the exchange rates for 1 hour to avoid excessive API calls
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency: str = "USD") -> Dict[str, float]:
    """
    Get real-time exchange rates from ExchangeRate-API
    Documentation: https://www.exchangerate-api.com/docs
    """
    try:
        # Replace with your API key from https://www.exchangerate-api.com/
        API_KEY = st.secrets["EXCHANGE_RATE_API_KEY"]
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
        
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"]
        else:
            raise Exception("Failed to fetch exchange rates")
            
    except Exception as e:
        st.warning(f"⚠️ Could not fetch real-time exchange rates: {str(e)}. Using fallback rates.")
        # Fallback to static rates if API fails
        return CURRENCY_RATES

# Fallback currency rates (used when API is unavailable)
CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.35,
    "AUD": 1.52,
    "JPY": 151.50,
    "CHF": 0.90,
    "NZD": 1.65,
    "CNY": 7.23,
    "INR": 83.34
}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert amount between currencies using real-time exchange rates
    """
    if from_currency == to_currency:
        return amount
        
    try:
        # Get real-time rates
        rates = get_exchange_rates(base_currency="USD")
        
        # Convert to USD first (if not already in USD)
        if from_currency != "USD":
            amount_usd = amount / rates[from_currency]
        else:
            amount_usd = amount
            
        # Convert from USD to target currency
        if to_currency != "USD":
            final_amount = amount_usd * rates[to_currency]
        else:
            final_amount = amount_usd
            
        return final_amount
        
    except Exception as e:
        st.warning(f"⚠️ Error in currency conversion: {str(e)}. Using fallback rates.")
        # Fallback to static rates if conversion fails
        if from_currency != "USD":
            amount_usd = amount / CURRENCY_RATES[from_currency]
        else:
            amount_usd = amount
            
        if to_currency != "USD":
            final_amount = amount_usd * CURRENCY_RATES[to_currency]
        else:
            final_amount = amount_usd
            
        return final_amount 