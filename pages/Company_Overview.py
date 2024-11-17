import streamlit as st
import sys
import pandas as pd
sys.path.insert(0, '/Users/khushitaneja/Desktop/Ideathon/ideathonwithfinance')
from functions.overview import Overview

# Set the page configuration

# Check if a company has been selected
if "selected_company" not in st.session_state:
    st.error("No company selected. Please go back to the Home Page and select a company.")
else:
    selected_company = st.session_state.selected_company

    # Display the header and selected company name
    
    try:

        df = pd.read_csv("resources/Ticker_IDs.csv")
        # Set the ticker symbol
        # Create an instance of the Overview class
        overview = Overview(selected_company, df)
        # Load financial data
        overview.load_financial_data()
        # Process the data
        overview.process_data()
        # Get competitors
        overview.get_competitors()
        # Generate the dashboard
        overview.generate_dashboard()
    except Exception as e:
            # Handle any errors and display an error message
        st.error(f"An error occurred: {str(e)}")