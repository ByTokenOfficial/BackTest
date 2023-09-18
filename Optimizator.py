import pandas as pd
import BackTester
from Strategies.VolumeBasedStrategy import VolumeBased

class Optimizator(BackTester.BackTester):
    def __init__(self, filename, size_percentage=10, cash=1000000, commission=0.003):
        # 繼承
        super().__init__(filename=filename, size_percentage=size_percentage, cash=cash, commission=commission)
    
    def optimize_VolumeBased_strategy(self):
        # 設置優化參數，參數數量 5 * 6 * 6 * 6
        self.cerebro.optstrategy(
            VolumeBased,
            lookback_period=range(21, 30, 2),
            buy_threshold_percentage=range(10, 21, 2),
            sell_threshold_percentage=range(5, 21, 3),
            cooldown_period=range(1, 17, 3)
        )
        # 運行優化程序
        return self.cerebro.run()


    def generate_params_list(self, backtest):
        self.params_list = []

        for strategy_instance in backtest:
            self.analysis(backtest=strategy_instance[0])
            self.calculate_trade_info(trade_info=self.trade_info)
            self.params_list.append([
                strategy_instance[0].params.lookback_period,
                strategy_instance[0].params.buy_threshold_percentage,
                strategy_instance[0].params.sell_threshold_percentage,
                strategy_instance[0].params.cooldown_period,
                self.returns_info["rnorm100"],
                self.drawdown_info["max"]["drawdown"],
                self.sharpe_ratio["sharperatio"],
                self.trade_measure["trade_count"],
                self.trade_measure["won_count"],
                self.trade_measure["lost_count"],
                self.trade_measure["won_rate"],
                self.trade_measure["lost_rate"],
                self.trade_measure["profit_factor"]
            ])

    def save_params(self, filename):
        # 轉為 DataFrame 格式
        params_df = pd.DataFrame(
                        self.params_list,
                        columns=['lookback_period', 'buy_threshold_percentage', 'sell_threshold_percentage',
                                'cooldown_period', 'apy_percentage', 'max_drawdown_percentage', 'sharpe_ratio',
                                'trade_count', 'won_count', 'lost_count', 'won_rate', 'lost_rate', 'profit_factor']
                    )
        # 存儲為 CSV 檔案
        params_df.to_csv(f'{filename}.csv', index=False)

    
if __name__ == '__main__':
    file_list = ['btcusdt.csv', 'ethusdt.csv']
    file_name = ['btc_volbased_params', 'eth_volbased_params']
    # 優化 btcusdt.csv 的策略參數
    optimizator_1 = Optimizator(filename=file_list[0])
    backtest_btc = optimizator_1.optimize_VolumeBased_strategy()
    optimizator_1.generate_params_list(backtest=backtest_btc)
    optimizator_1.save_params(filename=file_name[0])