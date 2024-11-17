import streamlit as st
import sys
import pandas as pd
sys.path.insert(0, '/Users/tanishqgoyal/Desktop/Ideathon/Ideathon_submission')

from stocknews import StockNews 
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    page_title="Company Overview",
    page_icon=":chart_with_upwards_trend:",
    layout="centered"
)

if "selected_company" not in st.session_state:
    st.error("No company selected. Please go back to the Home Page and select a company.")
else:
    selected_company = st.session_state.selected_company
    
    # Create a tab for news
    news_tab, = st.tabs(["Top 10 News"])

    # Display the header and selected company name
    
    with news_tab:
        st.header(f'News of {selected_company}')
        sn = StockNews(selected_company, save_news=False)
        df_news = sn.read_rss()

        for i in range(10):

            with stylable_container(
                key="news_container",
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
                st.subheader(f'News {i+1}')
                st.write(df_news['published'][i])
                st.write(df_news['title'][i])
                st.write(df_news['summary'][i])
                title_sentiment = df_news['sentiment_title'][i]  # Fix the key name
                st.write(f'Title Sentiment: {title_sentiment}')
                news_sentiment = df_news['sentiment_summary'][i]  # Fix the key name
                st.write(f'News Sentiment: {news_sentiment}')
