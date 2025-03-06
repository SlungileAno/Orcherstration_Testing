import backtrader as bt
import yfinance as yf
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

# Function to fetch historical data
def get_data(symbol, interval="15m"):  
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=30)  
    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.columns = ["open", "high", "low", "close", "volume"]
    # df.index=df.index+pd.Timedelta(hours=2)
    # print(df.tail(20))
    return df


# Data Cleaning for removing nulls and duplicates
def clean_data(df):
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df


# Currency pairs
currencies = ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "EURGBP=X", "USDCAD=X"]

# Define the Breakout Strategy
class BreakoutStrategy(bt.Strategy):
    params = (("lookback", 60),)

    def __init__(self):
        self.highest_high = bt.indicators.Highest(self.data.high, period=self.params.lookback)
        self.lowest_low = bt.indicators.Lowest(self.data.low, period=self.params.lookback)
        self.trade_signals = []  

    def next(self):
        timestamp = self.data.datetime.datetime(0)
        currency_pair = self.data._name  

        highest_high = self.highest_high[0]
        lowest_low = self.lowest_low[0]
        close_price = self.data.close[0]

        if not self.position:
            if close_price > highest_high:
                signal = "buy"
            elif close_price < lowest_low:
                signal = "sell"
            else:
                signal = "hold"

            self.trade_signals.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type": signal,
                "price": close_price,
                "currency_pair": currency_pair
            })

    def get_trade_signals(self):
        return self.trade_signals

# Backtest function
def run_backtest():
    signals_data = []
    initial_cash = 10000
    
    for currency in currencies:
        try:
            cerebro = bt.Cerebro()
            data = bt.feeds.PandasData(dataname=get_data(currency))
            cerebro.adddata(data, name=currency)
            cerebro.addstrategy(BreakoutStrategy)
            cerebro.addsizer(bt.sizers.PercentSizer, percents=5)
            cerebro.broker.setcash(initial_cash)
            
            strategies = cerebro.run()
            signals_data.extend(strategies[0].get_trade_signals())
        
        except Exception as e:
            print(f"Error with {currency}: {str(e)}")

    return signals_data

# API route for backtest results
@app.route('/trade-signals', methods=['GET'])
def get_trade_signals():
    trade_signals = run_backtest()
    return jsonify(trade_signals)

if __name__ == '__main__':
    app.run(debug=True)