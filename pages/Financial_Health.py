import streamlit as st
import sys
import pandas as pd
sys.path.insert(0, '/Users/khushitaneja/Desktop/Ideathon/ideathonwithfinance')
from functions.Health import FinancialHealth
import yfinance as yf
from functions.chatbot import chat_interface
from streamlit_extras.stylable_container import stylable_container

# Set the page configuration
st.set_page_config(
    page_title="Company Overview",
    page_icon=":chart_with_upwards_trend:",
    layout="centered"
)
if "selected_company" not in st.session_state:
    st.error("No company selected. Please go back to the Home Page and select a company.")
else:
    selected_company = st.session_state.selected_company

    # Display the header and selected company name
    st.title("Financial Health Analysis")
    st.write(f"### Analysis for: **{selected_company}**")

    try:
            # Create an instance of FinancialHealth class
            financial_health = FinancialHealth(selected_company)
            st.plotly_chart(financial_health.display_health_analysis(), use_container_width=True)

            # Display detailed analysis points
            st.subheader("Detailed Analysis")
            for point in financial_health.detailed_analysis['detailed_points']:
                with stylable_container(
                key="summary_container",
                css_styles=[
                    """
                {
                background-color: #2c2c2c; /* Darker background color */
                color: #ffffff; /* White text for contrast */
                padding: 0.5em;
                border-radius: 1em;
                box-shadow: 0 4px 8px rgba(255, 255, 255, 0.1);
                }
                """
                ],
                ):
                    st.write(f"• {point}")

            st.write(f"**Overall Summary:** {financial_health.detailed_analysis['summary']}")

            # Display the metrics table
            st.subheader("Financial Metrics Table")
            st.plotly_chart(financial_health.create_metrics_table(), use_container_width=True)

            # Dropdown for selecting a metric
            st.subheader("Metric Trend Analysis")
            selected_metric = st.selectbox("Select a Metric:", financial_health.metrics.columns, index=0)

            # Display line chart for the selected metric
            st.plotly_chart(financial_health.create_line_chart(selected_metric), use_container_width=True)

            # Display bar chart for Debt to Equity Ratio
            st.subheader("Debt to Equity Analysis")
            st.plotly_chart(financial_health.create_bar_chart(), use_container_width=True)

            metrics_dict = financial_health.get_metrices_dic()

            # Example prompt format
            prompt = (f"Analyze the financial health of {selected_company} strictly based on the provided metrics data. "
            "Use only the given information to answer any questions. Here are the metrics:\n\n"
            )

            # Append each year's data to the prompt
            for year, values in metrics_dict.items():
                prompt += f"Year: {year}\n"
                for metric, value in values.items():
                    prompt += f"{metric}: {value}\n"
                prompt += "\n"
            # Output the prompt
            print(prompt)
            chat_interface(prompt)

    except Exception as e:
            # Handle any errors and display an error message
        st.error(f"An error occurred: {str(e)}")