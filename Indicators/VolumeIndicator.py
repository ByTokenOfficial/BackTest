import backtrader as bt

class VolumeIndicator(bt.Indicator):
    lines = ('buy_threshold', 'sell_upper_threshold', 'sell_lower_threshold')

    def __init__(self, lookback_period, buy_threshold_percentage, sell_threshold_percentage):
        # 最小計算週期
        self.addminperiod(lookback_period)
        # 計算交易量閾值
        avg_volume = bt.ind.SMA(self.data.volume, period=lookback_period)
        self.lines.buy_threshold = avg_volume * (1 + (buy_threshold_percentage / 100))
        self.lines.sell_upper_threshold = avg_volume * (1 + (sell_threshold_percentage / 100))
        self.lines.sell_lower_threshold = avg_volume * (1 - (sell_threshold_percentage / 100))