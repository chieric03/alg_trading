from backtesting import Strategy
from backtesting.lib import crossover
import talib

class RsiAtrExitStrategy(Strategy):
    """
    An RSI Mean Reversion strategy with ATR-based Stop Loss and Take Profit.

    Enters long when RSI crosses below the lower threshold (oversold).
    Enters short when RSI crosses above the upper threshold (overbought).
    Exits are based on ATR multiples.
    """
    # Strategy parameters
    rsi_period = 14
    rsi_lower = 30
    rsi_upper = 70
    atr_period = 14
    atr_sl_mult = 1.5 # Stop Loss multiplier for ATR
    atr_tp_mult = 3.0 # Take Profit multiplier for ATR

    def init(self):
        """
        Initialize the strategy indicators.
        """
        # Ensure data columns are correctly named (Open, High, Low, Close)
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        # Calculate indicators
        self.rsi = self.I(talib.RSI, close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=self.atr_period)

    def next(self):
        """
        Define the trading logic for the next bar.
        """
        price = self.data.Close[-1]
        current_atr = self.atr[-1]

        # Check if we have enough data and valid ATR
        if len(self.rsi) < 1 or len(self.atr) < 1 or current_atr <= 0:
            return

        # Calculate SL and TP distances based on current ATR
        sl_distance = current_atr * self.atr_sl_mult
        tp_distance = current_atr * self.atr_tp_mult

        # Check for entry signals only if not already in a position
        if not self.position:
            # Long entry: RSI crosses below lower threshold
            if crossover(self.rsi_lower, self.rsi):
                sl = price - sl_distance
                tp = price + tp_distance
                self.buy(size=1, sl=sl, tp=tp)

            # Short entry: RSI crosses above upper threshold
            elif crossover(self.rsi, self.rsi_upper):
                sl = price + sl_distance
                tp = price - tp_distance
                self.sell(size=1, sl=sl, tp=tp)

# Example
if __name__ == '__main__':
    from backtesting import Backtest
    from backtesting_framework.data_handler.fetcher import fetch_data

    # Fetch sample data
    ticker = 'NQ=F'
    start_date = '2025-03-10'
    end_date = '2025-03-11'
    interval = '15m' # Using 15m for potentially better RSI signals than 1m
    data = fetch_data(ticker, start_date, end_date, interval)

    # IMPORTANT: Ensure columns are capitalized for backtesting.py
    if not data.empty:
        data.columns = [col.capitalize() for col in data.columns]
        if 'Adj_close' in data.columns:
             data = data.rename(columns={'Adj_close': 'Adj Close'})

        # Initialize and run backtest
        bt = Backtest(data, RsiAtrExitStrategy, cash=100_000, commission=.00025, exclusive_orders=True)
        stats = bt.run()
        print("\nBacktest Stats:")
        print(stats)
        # bt.plot() # Uncomment to plot results
    else:
        print("Could not run example backtest, data fetching failed.")
