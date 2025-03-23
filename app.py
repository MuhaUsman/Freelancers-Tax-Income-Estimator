import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page config
st.set_page_config(
    page_title="Freelancers' Tax & Income Estimator",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("Freelancers' Tax & Income Estimator")
st.markdown("""
    This app helps freelancers estimate their taxable income and tax liability.
    Enter your income sources and business expenses to get started.
""")

# Sidebar for tax bracket selection
with st.sidebar:
    st.header("Tax Settings")
    country = st.selectbox(
        "Select Country",
        ["United States", "United Kingdom", "Canada", "Australia", "Germany"]
    )
    
    # Tax brackets (example for US)
    tax_brackets = {
        "United States": [
            (0, 11000, 0.10),
            (11001, 44725, 0.12),
            (44726, 95375, 0.22),
            (95376, 182100, 0.24),
            (182101, 231250, 0.32),
            (231251, 578125, 0.35),
            (578126, float('inf'), 0.37)
        ],
        "United Kingdom": [
            (0, 12570, 0.20),
            (12571, 50270, 0.40),
            (50271, float('inf'), 0.45)
        ],
        "Canada": [
            (0, 53359, 0.15),
            (53360, 106717, 0.205),
            (106718, 165430, 0.26),
            (165431, 235675, 0.29),
            (235676, float('inf'), 0.33)
        ],
        "Australia": [
            (0, 18200, 0),
            (18201, 45000, 0.19),
            (45001, 120000, 0.325),
            (120001, 180000, 0.37),
            (180001, float('inf'), 0.45)
        ],
        "Germany": [
            (0, 10908, 0),
            (10909, 15999, 0.14),
            (16000, 62809, 0.42),
            (62810, float('inf'), 0.45)
        ]
    }

# Main content
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

# Calculate totals
total_income = sum(source["amount"] for source in income_sources)
total_expenses = sum(expense["amount"] for expense in expenses)
taxable_income = total_income - total_expenses

# Calculate tax
def calculate_tax(income, brackets):
    tax = 0
    for lower, upper, rate in brackets:
        if income > lower:
            taxable_amount = min(income - lower, upper - lower)
            tax += taxable_amount * rate
    return tax

tax_amount = calculate_tax(taxable_income, tax_brackets[country])
net_profit = taxable_income - tax_amount

# Display results
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
    fig2 = px.pie(
        values=[taxable_income, tax_amount],
        names=['Taxable Income', 'Tax'],
        title='Tax Distribution'
    )
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    # Net Profit Distribution Pie Chart
    fig3 = px.pie(
        values=[net_profit, tax_amount],
        names=['Net Profit', 'Tax'],
        title='Net Profit Distribution'
    )
    st.plotly_chart(fig3, use_container_width=True)

# Summary Table
st.header("Detailed Summary")
summary_data = {
    'Category': ['Total Income', 'Total Expenses', 'Taxable Income', 'Tax Amount', 'Net Profit'],
    'Amount': [total_income, total_expenses, taxable_income, tax_amount, net_profit]
}
summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

# Additional Insights
st.header("Financial Insights")
st.markdown(f"""
- **Effective Tax Rate**: {(tax_amount/taxable_income*100):.2f}%
- **Profit Margin**: {(net_profit/total_income*100):.2f}%
- **Expense Ratio**: {(total_expenses/total_income*100):.2f}%
""") 