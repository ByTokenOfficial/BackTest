import pandas as pd
import backtrader as bt
import backtrader.analyzers as btanalyzers
import datetime
from Strategies.VolumeBasedStrategy import VolumeBased
from Strategies.MACrossStrategy import MACross


class BackTester:
    def __init__(self, filename, flag='raw', multitimeframe=False, size_percentage=30, cash=1000000, commission=0.001):
        # 初始化數據
        if flag == 'dataframe':
            
            dtype = {
                'open': 'float64',
                'high': 'float64',
                'low': 'float64',
                'close': 'float64',
                'volume': 'float64'
            }
            # print('Loading data...')
            df = pd.read_csv(filename, dtype=dtype, parse_dates=['Time'], index_col='Time')
            # print(df.head())
            # print('Feeding data to backtrader...')
            self.data = bt.feeds.PandasData(
                                            dataname=df,
                                            timeframe=bt.TimeFrame.Minutes
                                            )
        else:
            self.data = bt.feeds.GenericCSVData(
                dataname=filename,
                fromdate=datetime.datetime(2020, 6, 24),
                todate=datetime.datetime(2023, 7, 25),
                nullvalue=0.0,
                dtformat=('%Y-%m-%d %H:%M:%S'),
                tmformat=('%H:%M:%S'),
                datetime=0,
                open=1,
                high=2,
                low=3,
                close=4,
                volume=5,
                openinterest=-1
            )


        # 初始化cerebro
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(cash)
        self.cerebro.broker.setcommission(commission)
        # 設置 Cheat-on-Open, Cheat-on-Close
        self.cerebro.broker.set_coo(True)
        self.cerebro.broker.set_coc(True)
        # 設置分析器
        self.cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe_ratio")
        self.cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(btanalyzers.Returns, _name="returns")
        self.cerebro.addanalyzer(btanalyzers.PeriodStats, _name="period_stats")
        self.cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name="trade_info")
        self.cerebro.addanalyzer(btanalyzers.PyFolio, _name="pyfolio")
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=size_percentage)

        if not multitimeframe:
            self.cerebro.adddata(self.data)
        else:
            self.cerebro.adddata(self.data, name="1h")
            self.cerebro.resampledata(self.data, name="4H", timeframe=bt.TimeFrame.Minutes, compression=240)
            self.cerebro.resampledata(self.data, name="1D", timeframe=bt.TimeFrame.Days)

    def backtest_strategy(self, strategy):
        self.cerebro.addstrategy(strategy)
        return self.cerebro.run(maxcpus=1)
    
    def analysis(self, backtest):
        self.sharpe_ratio = backtest.analyzers.sharpe_ratio.get_analysis()
        self.drawdown_info = backtest.analyzers.drawdown.get_analysis()
        self.returns_info = backtest.analyzers.returns.get_analysis()
        self.period_stats = backtest.analyzers.period_stats.get_analysis()
        self.trade_info = backtest.analyzers.trade_info.get_analysis()

    def plot_backtest_result(self):
        self.cerebro.plot()

    def calculate_trade_info(self, trade_info):
        self.trade_measure = dict()
        total_trade_count = trade_info['total']['closed']
        if total_trade_count > 1:
            won_data = trade_info['won']
            lost_data = trade_info['lost']
            won_count = won_data['total']
            lost_count = lost_data['total']
            gross_profit = won_data['pnl']['total']
            gross_lost = lost_data['pnl']['total']
            self.trade_measure['trade_count'] = total_trade_count
            self.trade_measure['won_count'] = won_count
            self.trade_measure['won_rate'] = 100 * (won_count / total_trade_count)
            self.trade_measure['lost_count'] = lost_count
            self.trade_measure['lost_rate'] = 100 * (lost_count / total_trade_count)
            self.trade_measure['profit_factor'] = -1 * (gross_profit / gross_lost)


if __name__ == '__main__':
    file_list = ['btcusdt.csv', 'ethusdt.csv', 'BTCUSDT_1m.csv', 'BTCUSDT_1D.csv', 'BTCUSDT_1H.csv']

    # backtester_1 = BackTester(file_list[-1], flag='dataframe', size_percentage=100)
    backtester_1 = BackTester(file_list[-1], flag='other', size_percentage=99)
    btc_backtest_result = backtester_1.backtest_strategy(MACross)
    backtester_1.analysis(backtest=btc_backtest_result[0])
    
    try:
        print(f'Sharpe Ratio: {backtester_1.sharpe_ratio["sharperatio"]:.2f}')
        print(f'Max Drawdown: {backtester_1.drawdown_info["max"]["drawdown"]:.2f}%')
        print(f'APY Percentage: {backtester_1.returns_info["rnorm100"]:.2f}%')
    except:
        raise Exception('No analysis data')

    backtester_1.calculate_trade_info(trade_info=backtester_1.trade_info)
    try:
        print(f'Trade Count: {backtester_1.trade_measure["trade_count"]}')
        print(f'Won Count: {backtester_1.trade_measure["won_count"]}')
        print(f'Lost Count: {backtester_1.trade_measure["lost_count"]}')
        print(f'Won Rate: {backtester_1.trade_measure["won_rate"]:.2f}%')
        print(f'Lost Rate: {backtester_1.trade_measure["lost_rate"]:.2f}%')
        print(f'Profit Factor: {backtester_1.trade_measure["profit_factor"]:.2f}')
    except:
        raise Exception('No trade data')

    backtester_1.plot_backtest_result()