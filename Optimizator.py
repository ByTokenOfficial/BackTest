import pandas as pd
import numpy as np
import BackTester
from bayes_opt import BayesianOptimization
from Strategies.VolumeBasedStrategy import VolumeBased
from Strategies.MACrossStrategy import MACross

class Optimizator(BackTester.BackTester):
    def __init__(self, strategy, filename, flag, size_percentage=10, cash=1000000, commission=0.001):
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
        # 記錄策略
        self.strategy = strategy

    def bayes_optimize(self, params_range, init_points=5, n_iter=100):
        # 記錄參數範圍
        self.params_range = params_range
        # 定義優化器並實例化
        opt = BayesianOptimization(
            f=self.bayes_objective_VB,
            pbounds=self.params_range,
            random_state=14240
        )
        # 使用優化器進行目標評估標準的最大化計算
        opt.maximize(
            init_points=init_points,
            n_iter=n_iter
        )
        # 記錄優化結果
        self.best_params = opt.max['params']
        self.best_score = opt.max['target']

        # 打印最佳參數組合
        print(f'Best Parameters: {self.best_params}')
        print(f'Best Score: {self.best_score}')

        # 返回最佳參數組合和最佳分數
        return self.best_params, self.best_score


    def bayes_objective_VB(self, lookback_period, buy_threshold_percentage, sell_threshold_percentage, cooldown_period):
        # 設定輸入參數
        lookback_period = round(lookback_period)
        buy_threshold_percentage = round(buy_threshold_percentage)
        sell_threshold_percentage = round(sell_threshold_percentage)
        cooldown_period = round(cooldown_period)
        # 定義評估器 -> x 對應 f(x)
        # 持續增加策略會導致效能有問題
        self.cerebro.addstrategy(
            self.strategy,
            lookback_period=lookback_period,
            buy_threshold_percentage=buy_threshold_percentage,
            sell_threshold_percentage=sell_threshold_percentage,
            cooldown_period=cooldown_period
        )
        backtest_result = self.cerebro.run()
        self.analysis(backtest=backtest_result[-1])
        # 定義評估標準 -> Returns Percentage / Max Drawdown
        returns_pct = float(self.returns_info['rtot']) # returns_pct = float(self.returns_info['rnorm100'])
        mdd = float(self.drawdown_info['max']['drawdown'])

        if (not np.isnan(mdd)) and (not np.isnan(returns_pct)) and (not np.isinf(mdd)) and (not np.isinf(returns_pct)):
            score = returns_pct / mdd
            # 返回評估標準值
            return score
        else:
            return 0

    def grid_search_optimize(self, params_range):
        # 記錄參數範圍
        self.params_range = params_range
        # Grid Search 最佳化
        self.cerebro.optstrategy(
            self.strategy,
            **self.params_range
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
    file_list = ['BTCUSDT_1D.csv']
    file_name = ['btc_volbased_params_new']
    optimization_method = 'bayes'
    # GridSearch 參數範圍表
    grid_search_params = {
        'lookback_period': range(21, 30, 2),
        'buy_threshold_percentage': range(10, 21, 2),
        'sell_threshold_percentage': range(5, 21, 3),
        'cooldown_period': range(1, 17, 3)
    }
    # 貝葉斯優化參數結果，輸入為 float，上下限閉區間
    bayes_opt_params = {
        'lookback_period': (15, 20),
        'buy_threshold_percentage': (1, 10),
        'sell_threshold_percentage': (1, 10),
        'cooldown_period': (5, 15)
    }
    # 優化 btcusdt.csv 的策略參數
    optimizator_1 = Optimizator(
        strategy=VolumeBased,
        filename=file_list[0],
        flag='dataframe',
        size_percentage=30
        )
    if optimization_method == 'bayes':
        best_params, best_score = optimizator_1.bayes_optimize(
                                        params_range=bayes_opt_params,
                                        init_points=5,
                                        n_iter=40
                                        )
    else:
        optimizator_1.grid_search_optimize(params_range=grid_search_params)
        optimizator_1.generate_params_list(backtest=optimizator_1.opt_results)
        optimizator_1.save_params(filename=file_name[0])