import backtrader as bt
from Indicators.VolumeIndicator import VolumeIndicator


class VolumeBased(bt.Strategy):
    # 設定參數
    params = (
        ('lookback_period', 25),
        ('buy_threshold_percentage', 10),
        ('sell_threshold_percentage', 5),
        ('cooldown_period', 10)
    )

    def __init__(self):
        # 紀錄訂單信息
        self.order = None
        # 紀錄交易bar
        self.bar_executed = None
        # 收盤價
        self.dataclose = self.datas[0].close
        # 成交量
        self.datavolume = self.datas[0].volume
        # 指標
        self.vol_ind = VolumeIndicator(
            self.data,
            lookback_period=self.params.lookback_period,
            buy_threshold_percentage=self.params.buy_threshold_percentage,
            sell_threshold_percentage=self.params.sell_threshold_percentage
        )
        
    def next(self):
        # 打印每日收盤價
        # self.log(f'Close: {self.dataclose[0]}')
        # 買入和賣出觸發條件（單個或多個）
        self.buy_condition = self.datavolume[0] > self.vol_ind.lines.buy_threshold[0]
        self.sell_condition =(self.datavolume[0] > self.vol_ind.lines.sell_upper_threshold) \
                            or (self.datavolume[0] < self.vol_ind.lines.sell_lower_threshold)
        if self.order:
            return 
        # 帳戶沒有部位
        if not self.position:
            # 進場條件
            if self.buy_condition and ((self.bar_executed is None) or ((len(self) - self.bar_executed) > self.params.cooldown_period)):
                self.log('BUY ' + ', Price: ' + str(self.dataclose[0]))
                # 使用開盤價買入標的
                self.order = self.buy(price=self.dataclose[0])
        # 有部位，賣出條件
        else:
            if self.sell_condition:
                # 印出買賣日期與價位
                self.log('SELL ' + ', Price: ' + str(self.dataclose[0]))
                # 使用下一根開盤價賣出標的
                self.order = self.close(price=self.dataclose[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'Buy Executed Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm}')
                self.params.entry_price = order.executed.price
                self.buy_price = order.executed.price
                self.buycommn = order.executed.comm
            elif order.issell():
                self.log(f'Sell Executed Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm}')
            #紀錄買的bar
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        
        #訂單執行後進行reset
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'Operation Profit, Gross Profit: {trade.pnl:.2f}, Net Profit: {trade.pnlcomm}')

    # 交易紀錄
    def log(self, txt, dt=None, doprint=False):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    # 優化參數用
    def stop(self, bayes=True):
        if bayes:
            return
        else:
            print(self.params.lookback_period, self.params.buy_threshold_percentage,
                self.params.sell_threshold_percentage, self.params.cooldown_period,
                self.broker.getvalue())