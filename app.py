import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import (
    TAX_BRACKETS, COMMON_DEDUCTIONS, RETIREMENT_LIMITS, CURRENCY_RATES,
    calculate_tax, calculate_quarterly_tax, get_tax_optimization_tips,
    calculate_monthly_goal, calculate_retirement_impact, adjust_for_inflation,
    convert_currency
)

# Page config and styling
st.set_page_config(
    page_title="Freelancers' Tax & Income Estimator",
    page_icon="💰",
    layout="wide"
)

# Hide Streamlit elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stGitHubButtonContainer {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .main {padding: 2rem;}
    .stButton>button {width: 100%;}
    .tax-tip {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("Freelancers' Tax & Income Estimator")
st.markdown("""
    This app helps freelancers estimate their taxable income, plan taxes, and set financial goals.
    Enter your income sources and business expenses to get started.
""")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    
    # Country and Currency Selection
    country = st.selectbox("Select Country", list(TAX_BRACKETS.keys()))
    currency = st.selectbox("Select Currency", list(CURRENCY_RATES.keys()))
    
    # Income Goal Setting
    st.header("Income Goals")
    annual_goal = st.number_input("Annual Income Goal", min_value=0, value=100000)
    
    # Retirement Planning
    st.header("Retirement Planning")
    retirement_account = st.selectbox("Retirement Account Type", list(RETIREMENT_LIMITS.keys()))
    retirement_contribution = st.slider(
        "Annual Contribution",
        0,
        RETIREMENT_LIMITS[retirement_account],
        RETIREMENT_LIMITS[retirement_account]//2
    )
    planning_years = st.slider("Planning Years", 1, 40, 20)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["Income & Expenses", "Tax Planning", "Deductions", "Financial Insights"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Income Sources")
        num_sources = st.number_input("Number of Income Sources", min_value=1, max_value=5, value=1)
        
        income_sources = []
        for i in range(num_sources):
            with st.expander(f"Income Source {i+1}"):
                source_name = st.text_input(f"Source Name {i+1}", key=f"source_name_{i}")
                amount = st.number_input(f"Amount {i+1}", min_value=0.0, key=f"amount_{i}")
                income_sources.append({"name": source_name, "amount": amount})
    
    with col2:
        st.header("Business Expenses")
        num_expenses = st.number_input("Number of Expense Categories", min_value=1, max_value=5, value=1)
        
        expenses = []
        for i in range(num_expenses):
            with st.expander(f"Expense Category {i+1}"):
                expense_name = st.text_input(f"Category Name {i+1}", key=f"expense_name_{i}")
                amount = st.number_input(f"Amount {i+1}", min_value=0.0, key=f"expense_amount_{i}")
                expenses.append({"name": expense_name, "amount": amount})

with tab2:
    st.header("Tax Planning")
    
    # Calculate totals
    total_income = sum(source["amount"] for source in income_sources)
    total_expenses = sum(expense["amount"] for expense in expenses)
    
    # Quarterly Tax Estimates
    st.subheader("Quarterly Tax Estimates")
    quarterly_taxes = calculate_quarterly_tax(total_income, calculate_tax(total_income - total_expenses, TAX_BRACKETS[country]))
    
    # Display quarterly tax table
    quarterly_df = pd.DataFrame.from_dict(quarterly_taxes, orient='index')
    st.dataframe(quarterly_df, use_container_width=True)
    
    # Tax Optimization Tips
    st.subheader("Tax Optimization Tips")
    tips = get_tax_optimization_tips(total_income, expenses, {})
    for tip in tips:
        st.markdown(f'<div class="tax-tip">💡 {tip}</div>', unsafe_allow_html=True)

with tab3:
    st.header("Tax Deductions")
    
    # Common deductions checklist
    st.subheader("Common Freelancer Deductions")
    selected_deductions = {}
    
    for deduction, details in COMMON_DEDUCTIONS.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{deduction}**")
            st.markdown(f"_{details['description']}_")
        with col2:
            if details['type'] == 'percentage':
                value = st.slider(f"{deduction} %", 0, 100, 0, key=f"deduction_{deduction}")
            else:
                value = st.number_input(f"{deduction} Amount", min_value=0.0, key=f"deduction_{deduction}")
            if value > 0:
                selected_deductions[deduction] = value

with tab4:
    st.header("Financial Insights")
    
    # Monthly goal calculations
    goal_calculations = calculate_monthly_goal(annual_goal, 0.25)  # Assuming 25% tax rate
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Income Goal Breakdown")
        st.metric("Monthly Target (Before Tax)", f"${goal_calculations['monthly_before_tax']:,.2f}")
        st.metric("Monthly Target (After Tax)", f"${goal_calculations['monthly_after_tax']:,.2f}")
    
    with col2:
        st.subheader("Retirement Projections")
        retirement_impact = calculate_retirement_impact(retirement_contribution, planning_years)
        st.metric("Projected Retirement Savings", f"${retirement_impact['future_value']:,.2f}")
        st.metric("Annual Tax Savings", f"${retirement_impact['tax_savings']:,.2f}")

# Financial Summary
st.header("Financial Summary")

# Create three columns for the charts
col1, col2, col3 = st.columns(3)

with col1:
    # Income vs Expenses Bar Chart
    fig1 = go.Figure(data=[
        go.Bar(name='Income', x=['Total'], y=[total_income], marker_color='green'),
        go.Bar(name='Expenses', x=['Total'], y=[total_expenses], marker_color='red')
    ])
    fig1.update_layout(title='Income vs Expenses')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Tax Distribution Pie Chart
    taxable_income = total_income - total_expenses
    tax_amount = calculate_tax(taxable_income, TAX_BRACKETS[country])
    fig2 = px.pie(
        values=[taxable_income - tax_amount, tax_amount],
        names=['Net Income', 'Tax'],
        title='Tax Distribution'
    )
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    # Deductions Breakdown
    deduction_values = list(selected_deductions.values())
    deduction_names = list(selected_deductions.keys())
    if deduction_values:
        fig3 = px.pie(
            values=deduction_values,
            names=deduction_names,
            title='Deductions Breakdown'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Add deductions to see the breakdown")

# Summary Table
st.header("Detailed Summary")
summary_data = {
    'Category': ['Total Income', 'Total Expenses', 'Taxable Income', 'Tax Amount', 'Net Profit'],
    'Amount': [
        total_income,
        total_expenses,
        taxable_income,
        tax_amount,
        taxable_income - tax_amount
    ]
}
summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

# Currency Conversion
if currency != "USD":
    st.header("Currency Conversion")
    converted_summary = summary_df.copy()
    converted_summary['Amount'] = converted_summary['Amount'].apply(
        lambda x: convert_currency(x, "USD", currency)
    )
    st.dataframe(converted_summary, use_container_width=True)

# Inflation Impact
st.header("Inflation Impact")
inflation_years = st.slider("Project inflation impact (years)", 1, 10, 5)
inflation_adjusted = adjust_for_inflation(taxable_income - tax_amount, inflation_years)
st.metric(
    f"Purchasing Power in {inflation_years} years",
    f"${inflation_adjusted:,.2f}",
    f"${inflation_adjusted - (taxable_income - tax_amount):,.2f}"
) 