import streamlit as st
import pandas as pd

# Set the page configuration
st.set_page_config(
    page_title="Finance Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="centered"
)

# Load company list from a CSV file
companies_df = pd.read_csv('resources/companies.csv', header=None)
companies = companies_df[0].tolist()  # Convert to a list

# Custom header with emojis for visual appeal
st.title("📊 Finance 101")
st.subheader("Analyze Your Favorite Companies in Just a Click!")

# Add a description or instructions for better user guidance
st.write("Select a company from the dropdown menu below to get started.")

# Dropdown for selecting a company
selected_company = st.selectbox("🔍 Choose a Company to Analyze:", companies)

# Button to navigate to the Overview Page
if st.button("Let's Go! 🚀"):
    # Store the selected company in Streamlit's session state
    st.session_state.selected_company = selected_company

    # Optionally, you can also use an info message to let the user know they're being redirected
    st.info("You are all set!! choose a page from the sidebar to view detailed analysis😎")