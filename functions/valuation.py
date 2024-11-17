import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from functions.chatbot import chat_interface

# Define the ValuationDashboard class
class ValuationDashboard:
    def __init__(self, ticker, df):
        self.ticker = ticker.upper()  # Use the provided ticker
        self.df = df
        self.stock = None
        self.balance_sheet = None
        self.income_statement = None
        self.cash_flow = None
        self.dcf_result = None
        self.shares_outstanding = None

    def load_financial_data(self):
        self.stock = yf.Ticker(self.ticker)
        self.balance_sheet = self.stock.balance_sheet
        self.income_statement = self.stock.financials
        self.cash_flow = self.stock.cashflow
        # Return False if any financial data is missing or empty
        return not (self.balance_sheet.empty or self.income_statement.empty or self.cash_flow.empty)

    def calculate_dcf(self, wacc, terminal_growth_rate, growth_rate, years):
        try:
            # Extract relevant financial data
            ebit = self.income_statement.loc['EBIT'].iloc[0]
            tax_expense = self.income_statement.loc['Tax Provision'].iloc[0]
            depreciation = self.cash_flow.loc['Depreciation And Amortization'].iloc[0]
            capex = self.cash_flow.loc['Capital Expenditure'].iloc[0]
            change_in_working_capital = self.cash_flow.loc['Change In Working Capital'].iloc[0]
            total_debt = self.balance_sheet.loc['Total Debt'].iloc[0]
            cash = self.balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        except Exception as e:
            st.error(f"Error extracting financial data: {e}")
            return False

        # Calculate key financial metrics
        tax_rate = tax_expense / ebit if ebit != 0 else 0
        nopat = ebit * (1 - tax_rate)
        fcf = nopat + depreciation - capex - change_in_working_capital

        # Forecast future Free Cash Flows and calculate Terminal Value
        future_fcfs = [fcf * (1 + growth_rate) ** i for i in range(1, years + 1)]
        terminal_value = future_fcfs[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)

        # Discount future Free Cash Flows to present value
        discounted_fcfs = [fcf / (1 + wacc) ** i for i, fcf in enumerate(future_fcfs, start=1)]
        pv_terminal_value = terminal_value / (1 + wacc) ** years

        # Calculate Enterprise Value and Equity Value
        enterprise_value = sum(discounted_fcfs) + pv_terminal_value
        equity_value = enterprise_value - total_debt + cash
        self.shares_outstanding = self.stock.info.get('sharesOutstanding', 1)  # Avoid division by zero
        intrinsic_value_per_share = equity_value / self.shares_outstanding

        # Save DCF results
        self.dcf_result = {
            'Intrinsic Value per Share': intrinsic_value_per_share,
            'Enterprise Value': enterprise_value,
            'Equity Value': equity_value,
            'Future FCFs': future_fcfs,
            'Discounted FCFs': discounted_fcfs,
            'Terminal Value': terminal_value,
            'PV of Terminal Value': pv_terminal_value,
            'WACC': wacc,
            'Growth Rate': growth_rate,
            'Terminal Growth Rate': terminal_growth_rate,
            'NOPAT': nopat,
            'FCF': fcf,
        }
        return True
         

    def generate_dashboard(self):
        # Set the main title
        

        # Create layout with columns for input parameters
        col1, col2 = st.columns([1, 1])

        with col1:
            st.header("Input Parameters")
            wacc = st.slider("Discount Rate (WACC)", min_value=0.01, max_value=0.20, value=0.08, step=0.005)
            growth_rate = st.slider("Growth Rate", min_value=0.00, max_value=0.20, value=0.03, step=0.005)
            terminal_growth_rate = st.slider("Terminal Growth Rate", min_value=0.00, max_value=0.05, value=0.02, step=0.005)
            years = st.slider("Projection Years", min_value=1, max_value=10, value=5, step=1)

        # Explanation of Parameters
        with col2:
            st.markdown("### Parameter Descriptions")
            st.markdown("<span style='color: red;'>These input parameters adjust the growth assumptions and risk factors used to calculate the company's intrinsic value in the DCF model.</span>", unsafe_allow_html=True)
            st.write("**Discount Rate (WACC):** The average rate of return required by investors. A higher rate reflects greater risk.")
            st.write("**Growth Rate:** The annual increase expected in free cash flows over the projection period.")
            st.write("**Terminal Growth Rate:** The rate at which the company’s cash flows are expected to grow indefinitely after the projection period.")
            st.write("**Projection Years:** The number of years over which future cash flows are projected.")

        # Load financial data and perform DCF calculation
        if not self.load_financial_data():
            st.error("Failed to load financial data. Please try a different ticker.")
            return

        if not self.calculate_dcf(wacc, terminal_growth_rate, growth_rate, years):
            return

        # Improved Investment Insight
        st.markdown("### Investment Insight")
        intrinsic_value = self.dcf_result['Intrinsic Value per Share']
        current_price = self.stock.info.get('currentPrice', None)

        if current_price:
            upside = ((intrinsic_value - current_price) / current_price) * 100
            if intrinsic_value > current_price:
                st.markdown(
                    f"- **Intrinsic Value per Share**: ${intrinsic_value:.2f}\n"
                    f"- **Current Market Price**: ${current_price:.2f}\n"
                    f"- **Status**: **Undervalued**\n"
                    f"- **Upside Potential**: {upside:.2f}%\n"
                    f"Consider investing as there is room for potential growth."
                )
            else:
                st.markdown(
                    f"- **Intrinsic Value per Share**: ${intrinsic_value:.2f}\n"
                    f"- **Current Market Price**: ${current_price:.2f}\n"
                    f"- **Status**: **Overvalued**\n"
                    f"- **Downside Risk**: {abs(upside):.2f}%\n"
                    f"Exercise caution and wait for a more favorable price."
                )

        # Display additional financial metrics in a row
        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        col3.metric("Shares Outstanding", f"{self.shares_outstanding:,}")
        col4.metric("Equity Value", f"${self.dcf_result['Equity Value'] / 1e9:.2f}B")
        col5.metric("Enterprise Value", f"${self.dcf_result['Enterprise Value'] / 1e9:.2f}B")

        # Display future FCFs and discounted FCFs
        fcf_df = pd.DataFrame({
            'Year': list(range(1, years + 1)),
            'Future FCF': self.dcf_result['Future FCFs'],
            'Discounted FCF': self.dcf_result['Discounted FCFs']
        })
        st.table(fcf_df)

        # Plot future FCFs
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=fcf_df['Year'],
            y=fcf_df['Future FCF'],
            name='Future FCF',
            marker_color='teal'
        ))
        fig.add_trace(go.Bar(
            x=fcf_df['Year'],
            y=fcf_df['Discounted FCF'],
            name='Discounted FCF',
            marker_color='coral'
        ))
        fig.update_layout(
            title='Future Free Cash Flows',
            xaxis_title='Year',
            yaxis_title='Cash Flow',
            barmode='group'
        )
        st.plotly_chart(fig)
        print(self.dcf_result)
        chat_interface(f"Comapay name is {self.ticker}Using only the provided company analysis data, generate a detailed explanation for each financial metric or calculation. Do not include any external information or general definitions that aren't specifically based on the analysis provided. Answer strictly within the context of the following data and metrics: comapny name is{self.dcf_result}Provide clear and concise explanations for each metric or calculation while staying within the bounds of the given data.")



