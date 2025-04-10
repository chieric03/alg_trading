import argparse
import importlib
import pandas as pd
import re
from backtesting import Backtest

# Import framework components
from data_handler.fetcher import fetch_data
from reporting.optimizer_plots import plot_optimization_heatmap

# Helper function to convert CamelCase to snake_case
def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def run():
    parser = argparse.ArgumentParser(description="Run backtests for algorithmic trading strategies.")

    # Required arguments
    parser.add_argument("strategy_name", help="Name of the strategy class (e.g., EmaCrossStrategy).")
    parser.add_argument("ticker", help="Ticker symbol (e.g., NQ=F, AAPL).")
    parser.add_argument("start_date", help="Start date for backtest (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date for backtest (YYYY-MM-DD).")

    # Optional arguments
    parser.add_argument("-i", "--interval", default="1d", help="Data interval (e.g., 1m, 15m, 1h, 1d). Default: 1d")
    parser.add_argument("-c", "--cash", type=int, default=100_000, help="Initial cash for backtest. Default: 100,000")
    parser.add_argument("--commission", type=float, default=0.0002, help="Commission per trade. Default: 0.0002")
    parser.add_argument("--optimize", action="store_true", help="Run optimization instead of a single backtest.")
    parser.add_argument("--plot", action="store_true", help="Show the backtesting plot after running.")
    parser.add_argument("--heatmap", nargs=2, metavar=('PARAM1', 'PARAM2'),
                        help="Generate optimization heatmap for PARAM1 vs PARAM2 after optimizing.")

    args = parser.parse_args()

    # --- 1. Fetch Data ---
    print(f"\n--- Fetching Data for {args.ticker} ---")
    data = fetch_data(args.ticker, args.start_date, args.end_date, args.interval)

    if data.empty:
        print("Exiting: Data fetching failed.")
        return

    # --- 2. Preprocess Data for backtesting.py ---
    # backtesting.py expects columns: Open, High, Low, Close, Volume
    print("\n--- Preprocessing Data ---")
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in data.columns for col in required_cols):
         print(f"Warning: Data missing one or more required columns: {required_cols}")
         print(f"Available columns: {list(data.columns)}")
         # Attempt to proceed if core OHLC are present
         if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
              print("Error: Core OHLC columns missing. Exiting.")
              return
         else:
              print("Proceeding without Volume column if missing...")
              if 'volume' not in data.columns:
                   data['volume'] = 0 # Add dummy volume if missing


    # Capitalize columns for backtesting.py
    data.columns = [col.capitalize() for col in data.columns]
    # Rename Adj_close back if needed, though usually not used directly in strategy
    if 'Adj_close' in data.columns:
         data = data.rename(columns={'Adj_close': 'Adj Close'})
    print("Capitalized column names for backtesting.py.")
    print("Data head after preprocessing:\n", data.head())


    # --- 3. Load Strategy ---
    print(f"\n--- Loading Strategy: {args.strategy_name} ---")
    try:
        # Convert CamelCase strategy name to snake_case module name
        # e.g., EmaCrossStrategy -> ema_cross
        strategy_file_base = camel_to_snake(args.strategy_name.replace('Strategy', ''))
        module_name = f"strategies.{strategy_file_base}"
        try:
            strategy_module = importlib.import_module(module_name)
            StrategyClass = getattr(strategy_module, args.strategy_name)
            print(f"Successfully loaded {args.strategy_name} from {module_name}.py")
        except ModuleNotFoundError:
            print(f"Error: Strategy module '{module_name}.py' not found in 'strategies' directory.")
            return
        except AttributeError:
            print(f"Error: Strategy class '{args.strategy_name}' not found within '{module_name}.py'.")
            return
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return
    except ModuleNotFoundError:
        print(f"Error: Strategy module '{module_name}.py' not found in 'strategies' directory.")
        return
    except AttributeError:
        print(f"Error: Strategy class '{args.strategy_name}' not found within '{module_name}.py'.")
        return
    except Exception as e:
        print(f"Error loading strategy: {e}")
        return

    # --- 4. Initialize Backtest ---
    print("\n--- Initializing Backtest ---")
    bt = Backtest(data, StrategyClass, cash=args.cash, commission=args.commission, exclusive_orders=True)

    # --- 5. Run Backtest or Optimization ---
    if args.optimize:
        print("\n--- Running Optimization ---")
        # TODO: Define optimization parameters dynamically or based on strategy
        # For now, hardcoding for EmaCrossStrategy as an example
        if args.strategy_name == 'EmaCrossStrategy':
            print("Optimizing EmaCrossStrategy parameters...")
            # Define optimization parameters and capture their names
            optimization_params = {
                'short_period': range(8, 20, 2),
                'long_period': range(20, 50, 5),
                'point_tp': range(10, 40, 5),
                'point_sl': range(5, 25, 5)
            }
            optimization_param_names = list(optimization_params.keys()) # Capture names

            stats, heatmap_data = bt.optimize(
                **optimization_params, # Unpack the dict
                constraint=lambda p: p.point_tp > p.point_sl and p.short_period < p.long_period,
                maximize='Equity Final [$]',
                method='sambo',
                max_tries=50, # Limit tries for non-grid methods
                return_optimization=True # Crucial for heatmap
            )
            print("\n--- Optimization Results ---")
            print("Best Stats:")
            print(stats)
            print("\nBest Parameters:")
            print(stats['_strategy'])

            # --- 6. Generate Heatmap (if requested) ---
            if args.heatmap and heatmap_data:
                print(f"\n--- Generating Heatmap for {args.heatmap[0]} vs {args.heatmap[1]} ---")
                # --- Debugging Prints (can be removed later) ---
                print(f"Debug: Type of heatmap_data: {type(heatmap_data)}")
                print(f"Debug: Has xv? {hasattr(heatmap_data, 'xv')}")
                print(f"Debug: Has funv? {hasattr(heatmap_data, 'funv')}")
                # --- End Debugging Prints ---
                plot_optimization_heatmap(
                    opt_result=heatmap_data,
                    all_param_names=optimization_param_names, # Pass the list of names
                    param1_name=args.heatmap[0],
                    param2_name=args.heatmap[1],
                    metric_name=stats.index[stats.index.str.contains("Equity Final", case=False)][0] # Get actual metric name
                )
            elif args.heatmap:
                 print("Heatmap requested, but optimization data is missing or failed.")

        # --- Add optimization parameters for the new strategy ---
        elif args.strategy_name == 'RsiAtrExitStrategy':
            print("Optimizing RsiAtrExitStrategy parameters...")
            optimization_params = {
                'rsi_period': range(10, 20, 2),
                'rsi_lower': range(20, 40, 5),
                'rsi_upper': range(60, 80, 5),
                'atr_period': range(10, 20, 2),
                'atr_sl_mult': [1.0, 1.5, 2.0, 2.5],
                'atr_tp_mult': [2.0, 2.5, 3.0, 3.5, 4.0]
            }
            optimization_param_names = list(optimization_params.keys())

            stats, heatmap_data = bt.optimize(
                **optimization_params,
                constraint=lambda p: p.rsi_lower < p.rsi_upper and p.atr_tp_mult > p.atr_sl_mult,
                maximize='Equity Final [$]',
                method='sambo',
                max_tries=100, # Increased tries for more params
                return_optimization=True
            )
            print("\n--- Optimization Results ---")
            print("Best Stats:")
            print(stats)
            print("\nBest Parameters:")
            print(stats['_strategy'])

            # Generate Heatmap (if requested)
            if args.heatmap and heatmap_data:
                print(f"\n--- Generating Heatmap for {args.heatmap[0]} vs {args.heatmap[1]} ---")
                plot_optimization_heatmap(
                    opt_result=heatmap_data,
                    all_param_names=optimization_param_names,
                    param1_name=args.heatmap[0],
                    param2_name=args.heatmap[1],
                    metric_name=stats.index[stats.index.str.contains("Equity Final", case=False)][0]
                )
            elif args.heatmap:
                 print("Heatmap requested, but optimization data is missing or failed.")
        # --- End of new strategy optimization block ---

        else:
            print(f"Optimization parameters not defined in run_backtest.py for strategy: {args.strategy_name}")
            print("Running single backtest with default parameters instead.")
            stats = bt.run()
            print("\n--- Backtest Results (Default Params) ---")
            print(stats)
            if args.plot:
                bt.plot()

    else:
        print("\n--- Running Single Backtest ---")
        stats = bt.run()
        print("\n--- Backtest Results ---")
        print(stats)
        if args.plot:
            bt.plot()

    print("\n--- Run Complete ---")

if __name__ == "__main__":
    run()
