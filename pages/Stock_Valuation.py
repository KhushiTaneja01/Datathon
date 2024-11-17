# Example usage in a Streamlit app
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
import matplotlib.pyplot as plt 

from functions.Stock import Dashboard, StockDataHandler, LSTMModel

# Set the page configuration
st.set_page_config(
    page_title="Company Overview",
    page_icon=":chart_with_upwards_trend:",
    layout="centered"
)


# Check if a company has been selected
if "selected_company" not in st.session_state:
    st.error("No company selected. Please go back to the Home Page and select a company.")
else:
    selected_company = st.session_state.selected_company

    # Display the header and selected company name
    st.title("Stock Valuation")
    st.write(f"### Analysis for: **{selected_company}**")

    try:
        # Create an instance of StockAnalysis and display metrics and analysis
        dashboard = Dashboard()
        dashboard.run()
    except Exception as e:
        # Handle any errors and display an error message
        st.error(f"An error occurred: {str(e)}")
