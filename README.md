# Algorithmic Trading

**Author**: Eric Chi  
**Email**: ericchi@g.ucla.edu

#### The main goal of this project is to learn and experiment as much as I can with the art of algorithmic trading. The goal right now is not to find my own edge, but to truly understand the parameters to creating one through coding preexisting strategies
#### A big chunk of the project deals with automating techincal analysis for buy/sell signals-- and backtesting these results to see how the algorithm performed.
---
##### There are many people who live and die by chart patterns technical analysis. There are also those who swear that its the astrology of trading and although these patterns are present; it is merely confirmation bias which proves these to be true.

##### Moreso than using these techniques and strategies as a whole truth, I am more interested in observing how often these patterns and why exactly they seem to occur. (Of course, I'm also interested in each strategy's PnL)

#### Reading List
- *Trading Systems and Methods* by Perry J. Kauffman
- *Max Dama on Automated Trading* ([link](http://isomorphisms.sdf.org/maxdama.pdf))
- *Building Winning Algorithmic Trading Systems* by Kevin Davey
- *Machine Learning for Trading by Stefan Jansen ([link](https://github.com/stefan-jansen/machine-learning-for-trading))* 

## Files:
- __intro.ipynb__ - This is the first notebook in the project. Used as an introduction to indicators, charting, signals using just pandas and plotly. I also try to explains basic indicators and how signals work. A way to scratch the surface of technical analysis. Also explains basic indicators like EMA and MACD. In each following individual usage of new indicators I will explain them
- __backtest_intro.ipynb__ - Getting a feel for the backtesting.py library


## Main framework (backtesting_framework)
- to run % python backtesting_framework/run_backtest.py
- e.g. % python backtesting_framework/run_backtest.py RsiAtrExitStrategy NQ=F 2025-03-10 2025-03-20 -i 15m  --plot
- Strategies classes are made in the form of ([documentation](https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html#gsc.tab=0))

run_backtest.py [-h] [-i INTERVAL] [-c CASH]
                       [--commission COMMISSION]
                       [--optimize] [--plot]
                       [--heatmap PARAM1 PARAM2]
                       strategy_name ticker start_date
                       end_date

positional arguments:
  - strategy_name         : Name of the strategy class (e.g.,
                        EmaCrossStrategy).

  - ticker                : Ticker symbol (e.g., NQ=F, AAPL).
  - start_date            : Start date for backtest (YYYY-MM-
                        DD).
  - end_date              End date for backtest (YYYY-MM-DD).

options:  
  -h, --help            : show this help message and exit  
  -i INTERVAL, --interval INTERVAL: 
                        Data interval (e.g., 1m, 15m, 1h,
                        1d). Default: 1d  
  -c CASH, --cash CASH  : Initial cash for backtest. Default:
                        100,000  
  --commission COMMISSION :
                        Commission per trade. Default:
                        0.0002  
  --optimize            : Run optimization instead of a single
                        backtest.  
  --plot                : Show the backtesting plot after
                        running.  
  --heatmap PARAM1 PARAM2: 
                        Generate optimization heatmap for
                        PARAM1 vs PARAM2 after optimizing.

### WIP
- creating a UI to streamline running framework