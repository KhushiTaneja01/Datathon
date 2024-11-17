import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st  # Added this line

class Overview:
    def __init__(self, ticker, df):
        self.ticker = ticker
        self.df = df
        self.stock = None
        self.balance_sheet = None
        self.cash_flow = None
        self.income_statement = None
        self.years = None
        self.competitors = None
        self.company_info = None
        self.profit_change_df = None

    def load_financial_data(self):
        # Use yfinance to get stock data
        self.stock = yf.Ticker(self.ticker)
        self.balance_sheet = self.stock.balance_sheet
        self.cash_flow = self.stock.cashflow
        self.income_statement = self.stock.financials

        # Check if data is retrieved
        if self.income_statement.empty:
            st.error(f"No financial data found for ticker '{self.ticker}'.")
            return

        # Drop '2020-09-30' columns if present
        self.balance_sheet = self.balance_sheet.drop(columns='2020-09-30', errors='ignore')
        self.cash_flow = self.cash_flow.drop(columns='2020-09-30', errors='ignore')
        self.income_statement = self.income_statement.drop(columns='2020-09-30', errors='ignore')

        # Get years from balance_sheet
        self.years = self.balance_sheet.columns.tolist()

    def process_data(self):
        # Calculate the yearly profit change for visualization
        if 'Net Income' not in self.income_statement.index:
            st.error("Net Income not found in income statement data.")
            return
        profit_change = self.income_statement.loc['Net Income'].diff().fillna(0)
        # Create a new DataFrame to store years and profit change
        self.profit_change_df = pd.DataFrame({
            'Year': self.income_statement.columns,
            'Profit Change': profit_change.values
        })

        # Get company information
        company_row = self.df.loc[self.df['Tickers'] == self.ticker]
        if company_row.empty:
            st.error(f"Ticker '{self.ticker}' not found in the DataFrame.")
            return
        company_name = company_row['Company Name'].values[0]
        state = company_row['stprma'].values[0]
        self.company_info = {
            "Company Name": company_name,
            "State": state
        }

    def get_competitors(self):
        # Get companies by SIC code
        company_row = self.df.loc[self.df['Tickers'] == self.ticker]
        if company_row.empty:
            st.error(f"Ticker '{self.ticker}' not found in the DataFrame.")
            return
        try:
            sic_code = company_row['sic'].values[0]
        except KeyError:
            st.error(f"SIC code not found for ticker '{self.ticker}'.")
            return
        # Filter companies with the same SIC code
        companies_with_same_sic = self.df[self.df['sic'] == sic_code]
        # Exclude the current company
        companies_with_same_sic = companies_with_same_sic[companies_with_same_sic['Tickers'] != self.ticker]
        if companies_with_same_sic.empty:
            st.warning("No competitors found with the same SIC code.")
            self.competitors = []
            return
        # Get a sample of competitors
        self.competitors = companies_with_same_sic['Company Name'].sample(n=min(5, len(companies_with_same_sic)), random_state=1).tolist()

    def generate_dashboard(self):
        # Streamlit App
        st.title("Company Overview")

        # Company Information Section
        st.header("Information")
        if self.company_info:
            st.write(f"**Company Name:** {self.company_info['Company Name']}")
            st.write(f"**State:** {self.company_info['State']}")
        else:
            st.write("Company information is not available.")

        # Competitor Analysis Section
        st.header("Competitors")
        if self.competitors:
            for comp in self.competitors:
                st.write(f"- {comp}")
        else:
            st.write("No competitors found.")

        # Profit Visualization Section
        st.header("Profit Growth Yearly")
        if self.profit_change_df is not None and not self.profit_change_df.empty:
            # Create columns for better layout
            cols = st.columns(len(self.profit_change_df))
            for idx, row in self.profit_change_df.iterrows():
                color = 'green' if row['Profit Change'] >= 0 else 'red'
                with cols[idx]:
                    st.markdown(
                        f"<div style='background-color:{color}; padding:10px; border-radius:5px; color:white; text-align:center;'>"
                        f"{row['Year']}: ${row['Profit Change'] / 1e9:,.2f}B"
                        f"</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.write("Profit change data is not available.")

        # Total Revenue Bar Chart
        st.header("Total Revenue Over Time")
        if 'Total Revenue' not in self.income_statement.index:
            st.error("Total Revenue not found in income statement data.")
            return
        fig = go.Figure(data=[
            go.Bar(
                x=self.income_statement.columns,
                y=self.income_statement.loc['Total Revenue'] / 1e9,  # Convert to billions
                name="Total Revenue",
                marker_color='teal'  # Use teal for the bar color
            )
        ])
        fig.update_layout(
            title={
                'text': "Total Revenue Over Time (in Billions)",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Year",
            yaxis_title="Total Revenue ($B)",
            template="plotly_dark",  # Use a dark template for a modern look
            plot_bgcolor="#1f2c3d",  # Dark background for the plot area
            paper_bgcolor="#1b2735",  # Dark background for the paper
            font=dict(color="white"),  # White text for better contrast
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='coral',  # Coral color for the axis line
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='coral'  # Coral color for tick labels
                )
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                linecolor='teal',  # Teal color for the y-axis line
                gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='teal'  # Teal color for y-axis tick labels
                )
            )
        )

        st.plotly_chart(fig)

