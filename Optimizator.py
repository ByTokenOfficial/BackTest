import pandas as pd
import BackTester
from Strategies.VolumeBasedStrategy import VolumeBased
from Strategies.MACrossStrategy import MACross

class Optimizator(BackTester.BackTester):
    def __init__(self, strategy, params_range, filename, flag, size_percentage=10, cash=1000000, commission=0.001):
        # 繼承
        super().__init__(
            filename=filename,
            flag=flag,
            size_percentage=size_percentage,
            cash=cash,
            commission=commission
            )
        # 默認評估標準
        self.measurement = [
            'apy_percentage',
            'max_drawdown_percentage',
            'sharpe_ratio',
            'trade_count',
            'won_count',
            'lost_count',
            'won_rate',
            'lost_rate',
            'profit_factor'
        ]
        # 記錄參數範圍
        self.params_range = params_range
        # 帶入對應策略及相關參數範圍
        self.cerebro.optstrategy(
            strategy,
            **params_range
        )
        # 記錄優化結果
        self.opt_results = self.cerebro.run()

    def generate_params_list(self, backtest):
        self.params_list = []

        for strategy_instance in backtest:
            self.analysis(backtest=strategy_instance[0])
            self.calculate_trade_info(trade_info=self.trade_info)
            params_dict = {}
            params = strategy_instance[0].params
            for attr in dir(params):
                if not attr.startswith("__"):
                    value = getattr(params, attr)
                    if isinstance(value, int):
                        params_dict[attr] = value
            params_set = [params_dict[k] for k in self.params_range.keys()]            
            info_set = [
                self.returns_info["rnorm100"],
                self.drawdown_info["max"]["drawdown"],
                self.sharpe_ratio["sharperatio"],
                self.trade_measure["trade_count"],
                self.trade_measure["won_count"],
                self.trade_measure["lost_count"],
                self.trade_measure["won_rate"],
                self.trade_measure["lost_rate"],
                self.trade_measure["profit_factor"]
            ]
            self.params_list.append(params_set + info_set)

    def save_params(self, filename):
        col1  = [k for k in self.params_range.keys()]
        # 轉為 DataFrame 格式
        params_df = pd.DataFrame(
                        self.params_list,
                        columns=col1+self.measurement
                    )
        # 存儲為 CSV 檔案
        params_df.to_csv(f'{filename}.csv', index=False)

    
if __name__ == '__main__':
    file_list = ['BTCUSDT_1H.csv']
    file_name = ['btc_volbased_params_new']
    # 參數範圍表
    params_range = {
        'lookback_period': range(21, 30, 2),
        'buy_threshold_percentage': range(10, 21, 2),
        'sell_threshold_percentage': range(5, 21, 3),
        'cooldown_period': range(1, 17, 3)
    }
    # 優化 btcusdt.csv 的策略參數
    optimizator_1 = Optimizator(
        strategy=VolumeBased,
        params_range=params_range,
        filename=file_list[0],
        flag='dataframe',
        size_percentage=30
        )
    # backtest_btc = optimizator_1.optimize_VolumeBased_strategy()
    optimizator_1.generate_params_list(backtest=optimizator_1.opt_results)
    optimizator_1.save_params(filename=file_name[0])