from backtesting import Strategy
from backtesting.lib import crossover
import talib

class EmaCrossStrategy(Strategy):
    """
    A simple EMA Crossover strategy.

    Enters long when the short EMA crosses above the long EMA.
    Enters short when the short EMA crosses below the long EMA.
    Uses fixed point-based stop loss and take profit.
    """
    # Strategy parameters (can be optimized)
    short_period = 12
    long_period = 26
    point_tp = 20  # Take profit in points
    point_sl = 10  # Stop loss in points

    def init(self):
        """
        Initialize the strategy indicators.
        """
        # Ensure data columns are correctly named (Open, High, Low, Close)
        # Note: Price data is accessed via self.data.Close, self.data.Open etc.
        close = self.data.Close
        self.short_ema = self.I(talib.EMA, close, self.short_period)
        self.long_ema = self.I(talib.EMA, close, self.long_period)

    def next(self):
        """
        Define the trading logic for the next bar.
        """
        price = self.data.Close[-1]

        # Check if we have enough data to calculate indicators
        if len(self.short_ema) < 2 or len(self.long_ema) < 2:
            return

        # Check for EMA crossover signals
        if crossover(self.short_ema, self.long_ema):
            # Short EMA crossed above Long EMA -> Buy signal
            if not self.position: # Only enter if not already in a position
                sl = price - self.point_sl
                tp = price + self.point_tp
                self.buy(size=1, sl=sl, tp=tp)

        elif crossover(self.long_ema, self.short_ema):
            # Short EMA crossed below Long EMA -> Sell signal
            if not self.position: # Only enter if not already in a position
                sl = price + self.point_sl
                tp = price - self.point_tp
                self.sell(size=1, sl=sl, tp=tp)



#Example usage:
if __name__ == '__main__':
    from backtesting import Backtest
    from backtesting_framework.data_handler.fetcher import fetch_data

    # Fetch sample data
    ticker = 'NQ=F'
    start_date = '2025-03-10'
    end_date = '2025-03-11'
    interval = '1m'
    data = fetch_data(ticker, start_date, end_date, interval)

    # IMPORTANT: Ensure columns are capitalized for backtesting.py
    if not data.empty:
        data.columns = [col.capitalize() for col in data.columns]
        # Rename Adj_close back if needed, though usually not used directly in strategy
        if 'Adj_close' in data.columns:
             data = data.rename(columns={'Adj_close': 'Adj Close'})


        # Initialize and run backtest
        bt = Backtest(data, EmaCrossStrategy, cash=100_000, commission=.00025, exclusive_orders=True)
        stats = bt.run()
        print("\nBacktest Stats:")
        print(stats)
        # bt.plot() # Uncomment to plot results
    else:
        print("Could not run example backtest, data fetching failed.")
