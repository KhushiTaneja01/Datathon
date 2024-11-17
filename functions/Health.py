import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class FinancialHealth:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.metrics = None
        self.analysis = ""
        self.health_score = 0
        self.health_status = ""
        self.detailed_analysis = {}
        self.fetch_and_calculate_metrics()

    def fetch_and_calculate_metrics(self):
        # Fetch financial statements
        balance_sheet = self.stock.balance_sheet
        cash_flow = self.stock.cashflow
        income_statement = self.stock.financials

        # Drop columns for the year 2020-09-30 if present
        # Drop both '2020-09-30' and '2019-09-30' columns from each DataFrame
        balance_sheet = balance_sheet.drop(columns=['2020-09-30', '2019-09-30'], errors='ignore')
        cash_flow = cash_flow.drop(columns=['2020-09-30', '2019-09-30'], errors='ignore')
        income_statement = income_statement.drop(columns=['2020-09-30', '2019-09-30'], errors='ignore')


        # Define years and format them to display only the year
        years = balance_sheet.columns.tolist()
        years_str = [str(pd.Timestamp(year).year) for year in years]

        # Initialize a DataFrame to store metrics
        self.metrics = pd.DataFrame(index=years_str, columns=[
            'Current Ratio',
            'Quick Ratio',
            'Working Capital',
            'Debt to Equity Ratio',
            'Debt to Assets Ratio',
            'Asset Turnover Ratio',
            'Return on Assets (ROA) (%)',
            'Return on Equity (ROE) (%)',
            'Net Debt'
        ])

        # Calculate metrics for each year
        for i, year in enumerate(years):
            year_str = years_str[i]
            year = pd.Timestamp(year)

            # Helper function to safely extract values
            def get_value(df, item, year):
                try:
                    return df.at[item, year]
                except KeyError:
                    return np.nan

            # Extract values
            current_assets = get_value(balance_sheet, 'Current Assets', year)
            current_liabilities = get_value(balance_sheet, 'Current Liabilities', year)
            inventory = get_value(balance_sheet, 'Inventory', year)
            total_assets = get_value(balance_sheet, 'Total Assets', year)
            total_debt = get_value(balance_sheet, 'Total Debt', year)
            shareholders_equity = get_value(balance_sheet, 'Stockholders Equity', year)
            cash_equiv = get_value(balance_sheet, 'Cash And Cash Equivalents', year)

            net_income = get_value(income_statement, 'Net Income', year)
            total_revenue = get_value(income_statement, 'Total Revenue', year)

            # Calculate Liquidity Ratios
            current_ratio = current_assets / current_liabilities if current_liabilities != 0 else np.nan
            quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities != 0 else np.nan
            working_capital = current_assets - current_liabilities

            # Calculate Leverage Ratios
            debt_to_equity = total_debt / shareholders_equity if shareholders_equity != 0 else np.nan
            debt_to_assets = total_debt / total_assets if total_assets != 0 else np.nan

            # Calculate Efficiency Ratios
            asset_turnover = total_revenue / total_assets if total_assets != 0 else np.nan

            # Calculate Profitability Ratios
            roa = (net_income / total_assets) * 100 if total_assets != 0 else np.nan
            roe = (net_income / shareholders_equity) * 100 if shareholders_equity != 0 else np.nan

            # Calculate Net Debt
            net_debt = total_debt - cash_equiv

            # Assign to metrics DataFrame
            self.metrics.loc[year_str, 'Current Ratio'] = round(current_ratio, 2)
            self.metrics.loc[year_str, 'Quick Ratio'] = round(quick_ratio, 2)
            self.metrics.loc[year_str, 'Working Capital'] = round(working_capital, 2)
            self.metrics.loc[year_str, 'Debt to Equity Ratio'] = round(debt_to_equity, 2)
            self.metrics.loc[year_str, 'Debt to Assets Ratio'] = round(debt_to_assets, 2)
            self.metrics.loc[year_str, 'Asset Turnover Ratio'] = round(asset_turnover, 2)
            self.metrics.loc[year_str, 'Return on Assets (ROA) (%)'] = round(roa, 2)
            self.metrics.loc[year_str, 'Return on Equity (ROE) (%)'] = round(roe, 2)
            self.metrics.loc[year_str, 'Net Debt'] = round(net_debt, 2)

        # Perform analysis
        self.analyze_metrics()

    def get_metrices_dic(self):
        return self.metrics.to_dict(orient='index')

    def analyze_metrics(self):
        analysis_list = []
        score = 0
        total_possible_score = 0

        # Analyze Current Ratio
        current_ratios = self.metrics['Current Ratio'].dropna()
        latest_current_ratio = current_ratios.iloc[-1] if not current_ratios.empty else np.nan

        # 1. Current Ratio Analysis (Max 20 points)
        if pd.notna(latest_current_ratio):
            total_possible_score += 20
            if latest_current_ratio >= 2:
                score += 20
                analysis_list.append(f"The company's Current Ratio is {latest_current_ratio}, indicating excellent liquidity. (20/20 points)")
            elif latest_current_ratio >= 1.5:
                score += 15
                analysis_list.append(f"The company's Current Ratio is {latest_current_ratio}, indicating strong liquidity. (15/20 points)")
            elif latest_current_ratio >= 1:
                score += 10
                analysis_list.append(f"The company's Current Ratio is {latest_current_ratio}, indicating adequate liquidity. (10/20 points)")
            else:
                analysis_list.append(f"The company's Current Ratio is {latest_current_ratio}, indicating potential liquidity issues. (0/20 points)")
        else:
            analysis_list.append("Current Ratio: Data not available")

        # Analyze Quick Ratio
        quick_ratios = self.metrics['Quick Ratio'].dropna()
        latest_quick_ratio = quick_ratios.iloc[-1] if not quick_ratios.empty else np.nan

        # 2. Quick Ratio Analysis (Max 15 points)
        if pd.notna(latest_quick_ratio):
            total_possible_score += 15
            if latest_quick_ratio >= 1.5:
                score += 15
                analysis_list.append(f"The company's Quick Ratio is {latest_quick_ratio}, indicating strong ability to meet short-term obligations. (15/15 points)")
            elif latest_quick_ratio >= 1:
                score += 10
                analysis_list.append(f"The company's Quick Ratio is {latest_quick_ratio}, indicating good ability to meet short-term obligations. (10/15 points)")
            elif latest_quick_ratio >= 0.5:
                score += 5
                analysis_list.append(f"The company's Quick Ratio is {latest_quick_ratio}, indicating moderate ability to meet short-term obligations. (5/15 points)")
            else:
                analysis_list.append(f"The company's Quick Ratio is {latest_quick_ratio}, indicating weak ability to meet short-term obligations. (0/15 points)")
        else:
            analysis_list.append("Quick Ratio: Data not available")

        # Analyze Debt to Equity Ratio
        debt_to_equity_ratios = self.metrics['Debt to Equity Ratio'].dropna()
        latest_debt_to_equity = debt_to_equity_ratios.iloc[-1] if not debt_to_equity_ratios.empty else np.nan

        # 3. Debt to Equity Ratio Analysis (Max 20 points)
        if pd.notna(latest_debt_to_equity):
            total_possible_score += 20
            if latest_debt_to_equity <= 0.5:
                score += 20
                analysis_list.append(f"The company's Debt to Equity Ratio is {latest_debt_to_equity}, indicating conservative financial structure. (20/20 points)")
            elif latest_debt_to_equity <= 1:
                score += 15
                analysis_list.append(f"The company's Debt to Equity Ratio is {latest_debt_to_equity}, indicating balanced financial structure. (15/20 points)")
            elif latest_debt_to_equity <= 2:
                score += 10
                analysis_list.append(f"The company's Debt to Equity Ratio is {latest_debt_to_equity}, indicating aggressive financial structure. (10/20 points)")
            else:
                analysis_list.append(f"The company's Debt to Equity Ratio is {latest_debt_to_equity}, indicating high financial risk. (0/20 points)")
        else:
            analysis_list.append("Debt to Equity Ratio: Data not available")

        # Analyze Return on Equity (ROE)
        roes = self.metrics['Return on Equity (ROE) (%)'].dropna()
        latest_roe = roes.iloc[-1] if not roes.empty else np.nan

        # 4. ROE Analysis (Max 25 points)
        if pd.notna(latest_roe):
            total_possible_score += 25
            if latest_roe >= 20:
                score += 25
                analysis_list.append(f"The company's Return on Equity is {latest_roe}%, indicating excellent profitability. (25/25 points)")
            elif latest_roe >= 15:
                score += 20
                analysis_list.append(f"The company's Return on Equity is {latest_roe}%, indicating strong profitability. (20/25 points)")
            elif latest_roe >= 10:
                score += 15
                analysis_list.append(f"The company's Return on Equity is {latest_roe}%, indicating good profitability. (15/25 points)")
            elif latest_roe >= 5:
                score += 10
                analysis_list.append(f"The company's Return on Equity is {latest_roe}%, indicating moderate profitability. (10/25 points)")
            else:
                analysis_list.append(f"The company's Return on Equity is {latest_roe}%, indicating poor profitability. (0/25 points)")
        else:
            analysis_list.append("Return on Equity: Data not available")

        # Analyze Asset Turnover Ratio
        asset_turnovers = self.metrics['Asset Turnover Ratio'].dropna()
        latest_asset_turnover = asset_turnovers.iloc[-1] if not asset_turnovers.empty else np.nan

        # 5. Asset Turnover Analysis (Max 20 points)
        if pd.notna(latest_asset_turnover):
            total_possible_score += 20
            if latest_asset_turnover >= 1.5:
                score += 20
                analysis_list.append(f"The company's Asset Turnover Ratio is {latest_asset_turnover}, indicating excellent operational efficiency. (20/20 points)")
            elif latest_asset_turnover >= 1:
                score += 15
                analysis_list.append(f"The company's Asset Turnover Ratio is {latest_asset_turnover}, indicating good operational efficiency. (15/20 points)")
            elif latest_asset_turnover >= 0.5:
                score += 10
                analysis_list.append(f"The company's Asset Turnover Ratio is {latest_asset_turnover}, indicating moderate operational efficiency. (10/20 points)")
            else:
                analysis_list.append(f"The company's Asset Turnover Ratio is {latest_asset_turnover}, indicating poor operational efficiency. (0/20 points)")
        else:
            analysis_list.append("Asset Turnover Ratio: Data not available")

        # Calculate final score and determine health status
        if total_possible_score > 0:
            score_percentage = (score / total_possible_score) * 100
        else:
            score_percentage = 0

        analysis_list.append(f"\nScoring Details:")
        analysis_list.append(f"Total Points Earned: {score}")
        analysis_list.append(f"Total Possible Points: {total_possible_score}")
        analysis_list.append(f"Final Score Percentage: {score_percentage:.2f}%")

        if score_percentage >= 80:
            health_status = "EXCELLENT"
            summary = "The company demonstrates strong financial health across most metrics."
        elif score_percentage >= 60:
            health_status = "GOOD"
            summary = "The company shows adequate financial health with some areas for improvement."
        else:
            health_status = "BAD"
            summary = "The company shows significant financial weaknesses that need attention."

        # Store the health score and status
        self.health_score = score_percentage
        self.health_status = health_status
        self.detailed_analysis = {
            'score': score_percentage,
            'status': health_status,
            'summary': summary,
            'detailed_points': analysis_list
        }

    def create_metrics_table(self):
        # Helper function to format large numbers
        def format_large_number(value):
            if pd.isna(value):
                return "-"
            elif abs(value) >= 1e9:
                return f"{value / 1e9:.2f}B"  # Billion
            elif abs(value) >= 1e6:
                return f"{value / 1e6:.2f}M"  # Million
            else:
                return f"{value:,.2f}"

        # Prepare the header and rows
        header = ["Year"] + self.metrics.columns.tolist()
        rows = []
        for year in self.metrics.index:
            # Apply the custom formatting to each value
            row = [year] + [format_large_number(value) for value in self.metrics.loc[year]]
            rows.append(row)

        # Create the table with the updated styles
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=header,
                fill_color='teal',  # Teal shade for the header
                align='center',
                font=dict(size=14, color='white'),  # White text for better contrast
                height=35  # Adjust header height
            ),
            cells=dict(
                values=list(zip(*rows)),
                fill_color='coral',  # Coral shade for the cells
                align='center',
                font=dict(size=12, color='black'),  # Adjusted font size for better readability
                height=30  # Adjust cell height
            )
        )])

        # Update layout to center the title and add padding
        fig.update_layout(
            title={
                'text': "Financial Metrics Overview",
                'x': 0.5,  # This centers the title horizontally
                'xanchor': 'center',  # This ensures the title is anchored in the center
                'yanchor': 'top'  # Anchors the title at the top
            },
            margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins for better spacing
        )

        return fig

    def create_bar_chart(self):
                # Sort the index in ascending order
        self.metrics = self.metrics.sort_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=self.metrics.index,
            y=self.metrics['Debt to Equity Ratio'],
            name='Debt to Equity Ratio',
            marker_color='coral'  # Use coral for the bar color
        ))

        fig.update_layout(
            title={
                'text': "Debt to Equity Ratio Over Time",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Year",
            yaxis_title="Debt to Equity Ratio",
            template="plotly_dark",  # Use a dark template for a modern look
            plot_bgcolor="#1f2c3d",  # Dark background for the plot area
            paper_bgcolor="#1b2735",  # Dark background for the paper
            font=dict(color="white"),  # White text for better contrast
            hovermode="x",  # Keep hovermode as "x"
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='teal',  # Teal color for the axis line
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='teal'  # Teal color for x-axis tick labels
                )
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                linecolor='coral',  # Coral color for the y-axis line
                gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='coral'  # Coral color for y-axis tick labels
                )
            )
        )

        return fig


    def create_line_chart(self, metric_name):
        self.metrics = self.metrics.sort_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.metrics.index,
            y=self.metrics[metric_name],
            mode='lines+markers',
            marker=dict(size=8, color='coral'),  # Coral color for markers
            line=dict(color='teal', width=2),  # Teal color for the line
            name=metric_name
        ))
        fig.update_layout(
            title={
                'text': f"{metric_name} Trend Over Time",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Year",
            yaxis_title=metric_name,
            template="plotly_dark",  # Use a dark template for a modern look
            plot_bgcolor="#1f2c3d",  # Dark background for the plot area
            paper_bgcolor="#1b2735",  # Dark background for the paper
            font=dict(color="white"),  # White text for better contrast
            hovermode="x",  # Keep hovermode as "x"
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='teal',  # Teal color for the x-axis line
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='teal'  # Teal color for x-axis tick labels
                )
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                linecolor='coral',  # Coral color for the y-axis line
                gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='coral'  # Coral color for y-axis tick labels
                )
            )
        )
        return fig

    def display_health_analysis(self):
        """
        Creates a gauge chart to display the health score
        """
        fig = go.Figure()

        # Create a gauge chart for the health score
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=self.health_score,
            title={'text': f"Financial Health Score: {self.health_status}"},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},  # White ticks for better contrast
                'bar': {'color': "teal"},  # Teal color for the gauge bar
                'steps': [
                    {'range': [0, 60], 'color': "coral"},  # Coral for lower health scores
                    {'range': [60, 80], 'color': "#FFD700"},  # Gold/yellow for moderate scores
                    {'range': [80, 100], 'color': "teal"}  # Teal for higher health scores
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},  # White threshold line for contrast
                    'thickness': 0.75,
                    'value': 60
                }
            }
        ))

        fig.update_layout(
            height=400,
            title={
            'text': "Company Financial Health Assessment",
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'yanchor': 'top'
                },
            title_x=0.5,
            font=dict(size=12, color='white'),  # White font for better readability
            paper_bgcolor="#1b2735",  # Dark background for the entire figure
            plot_bgcolor="#1f2c3d"  # Dark background for the plot area
        )

        return fig

