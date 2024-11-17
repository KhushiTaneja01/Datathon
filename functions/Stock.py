import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from functions.chatbot import chat_interface
class StockDataHandler:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def fetch_stock_data(self, stock_symbol):
        """Fetch stock data using yfinance"""
        try:
            start_date = dt.datetime(2000, 1, 1)
            end_date = dt.datetime(2024, 11, 1)
            
            # Fetch data from yfinance
            df = yf.download(stock_symbol, start=start_date, end=end_date)
            df.columns = df.columns.get_level_values(0)
            return df
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None

    def prepare_training_data(self, df, split_ratio=0.7):
        """Prepare data for training with consistent scaling"""
        # Fit the scaler on the entire dataset to ensure a consistent range
        self.scaler.fit(df[['Close']])

        training_size = int(len(df) * split_ratio)
        data_training = pd.DataFrame(df['Close'][:training_size])
        data_testing = pd.DataFrame(df['Close'][training_size:])

        # Scale both training and testing data using the fitted scaler
        data_training_scaled = self.scaler.transform(data_training)
        data_testing_scaled = self.scaler.transform(data_testing)

        x_train, y_train = [], []
        for i in range(100, len(data_training_scaled)):
            x_train.append(data_training_scaled[i-100:i, 0])
            y_train.append(data_training_scaled[i, 0])

        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        x_test, y_test = [], []
        for i in range(100, len(data_testing_scaled)):
            x_test.append(data_testing_scaled[i-100:i, 0])
            y_test.append(data_testing_scaled[i, 0])

        x_test = np.array(x_test)
        y_test = np.array(y_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        return x_train, y_train, x_test, y_test, data_testing['Close'][100:].values

class LSTMModel:
    def __init__(self):
        self.model = None
        
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        model = Sequential()
        model.add(LSTM(units=50, activation='relu', return_sequences=True, input_shape=(input_shape, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(units=60, activation='relu', return_sequences=True))
        model.add(Dropout(0.3))
        model.add(LSTM(units=80, activation='relu', return_sequences=True))
        model.add(Dropout(0.4))
        model.add(LSTM(units=120, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model
        return model

class Dashboard:
    def __init__(self):
        self.data_handler = StockDataHandler()
        self.lstm_model = LSTMModel()

    def plot_moving_averages_with_signals(self, df, symbol):
        """Plot stock price with moving averages and buy/sell signals"""
        df['Close'] = df['Close'].fillna(method='ffill')
        fast_ma = df['Close'].rolling(50).mean()
        slow_ma = df['Close'].rolling(200).mean()

        df['Buy_Signal'] = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        df['Sell_Signal'] = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Stock Price', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=fast_ma, name='50-Day MA', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=df.index, y=slow_ma, name='200-Day MA', line=dict(color='red')))

        fig.add_trace(go.Scatter(
            x=df[df['Buy_Signal']].index,
            y=df['Close'][df['Buy_Signal']],
            mode='markers',
            marker=dict(color='green', size=10, symbol='triangle-up'),
            name='Buy Signal'
        ))

        fig.add_trace(go.Scatter(
            x=df[df['Sell_Signal']].index,
            y=df['Close'][df['Sell_Signal']],
            mode='markers',
            marker=dict(color='red', size=10, symbol='triangle-down'),
            name='Sell Signal'
        ))

        fig.update_layout(
            title=f'{symbol} Stock Price with Buy/Sell Signals',
            yaxis_title='Stock Price (USD)',
            xaxis_title='Date'
        )
        return fig

    def plot_original_vs_predicted(self, original_prices, predicted_prices):
        """Plot original vs. predicted prices using Streamlit"""
        plt.figure(figsize=(12, 6))
        plt.plot(original_prices, label='Original Price', linewidth=1, color='blue')
        plt.plot(predicted_prices, label='Predicted Price', linewidth=1, color='orange')
        plt.title('Stock Price Prediction')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.legend()
        st.pyplot(plt)

    def run(self):
        """Main dashboard interface"""
        # Get the selected company from session state
        if "selected_company" not in st.session_state:
            st.error("No company selected. Please go back to the Home Page and select a company.")
            return
        
        stock_symbol = st.session_state.selected_company

        # Create tabs for different analyses
        tab1, tab2 = st.tabs(["Technical Analysis", "Price Prediction"])
        with tab1:
            st.subheader("Technical Analysis")
            df = self.data_handler.fetch_stock_data(stock_symbol)
            df_dict = df.tail().to_dict()
            chat_interface(f"company name is {stock_symbol} Using only the provided financial data, generate answers and insights for any queries related to stock performance metrics. Do not make any assumptions or use external information. Base your responses strictly on the data given below, which includes details on 'Adj Close', 'Close', 'High', 'Low', 'Open', and 'Volume' values for specific dates:{df_dict}")
            if df is not None and not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Recent Stock Data")
                    st.dataframe(df.tail())
                with col2:
                    st.write("Key Statistics")
                    current_price = df['Close'].iloc[-1]
                    price_change = df['Close'].pct_change().iloc[-1] * 100
                    st.metric("Current Price", f"${current_price:.2f}", 
                            f"{price_change:.2f}%")
                    
                st.subheader('Moving Averages with Buy/Sell Signals')
                signal_chart = self.plot_moving_averages_with_signals(df, stock_symbol)
                st.plotly_chart(signal_chart, use_container_width=True)

        with tab2:
            st.subheader("LSTM Price Prediction")
            
            if df is not None and not df.empty:
                with st.spinner('Training LSTM Model... This may take a few minutes.'):
                    # Prepare data and train model
                    x_train, y_train, x_test, y_test, original_prices = self.data_handler.prepare_training_data(df)
                    model = self.lstm_model.build_model(x_train.shape[1])
                    model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=1)
                
                st.success('Model Training Completed!')

                # Make predictions
                predicted_scaled = model.predict(x_test).flatten()

                # Manual scaling using the scaler factor
                scaler_factor = 1 / 0.0035166  # Example manual scaling factor
                predicted_prices = predicted_scaled * scaler_factor
                y_test = y_test * scaler_factor

                # Plot predictions
                st.subheader('Original vs. Predicted Prices')
                self.plot_original_vs_predicted(original_prices, predicted_prices)

                # Add prediction metrics
                mae = np.mean(np.abs(original_prices - predicted_prices))
                mape = np.mean(np.abs((original_prices - predicted_prices) / original_prices)) * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Mean Absolute Error", f"${mae:.2f}")
                with col2:
                    st.metric("Mean Absolute Percentage Error", f"{mape:.2f}%")

