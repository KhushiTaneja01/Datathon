import streamlit as st
import sys
import pandas as pd
sys.path.insert(0, '/Users/khushitaneja/Desktop/Ideathon/ideathonwithfinance')
from functions.valuation import ValuationDashboard


# Set the page configuration
# Set page configuration at the top
st.set_page_config(
    page_title="Company Valuation Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="centered"
)

intrinsic_value = 0
# Check if a company has been selected
if "selected_company" not in st.session_state:
    st.error("No company selected. Please go back to the Home Page and select a company.")
else:
    selected_company = st.session_state.selected_company

    # Display the header and selected company name
    st.title("Company Valuation")
    st.write(f"### Analysis for: **{selected_company}**")

    try:

        df = pd.read_csv("resources/Ticker_IDs.csv")
    # Create an instance of the ValuationDashboard class
    # The default ticker can be set to any valid ticker symbol
        dashboard = ValuationDashboard(selected_company, df)
        dashboard.generate_dashboard()  # Call
    except Exception as e:
            # Handle any errors and display an error message
        st.error(f"An error occurred: {str(e)}")