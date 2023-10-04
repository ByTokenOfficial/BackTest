import backtrader as bt
from datetime import timedelta

# Define your strategy
class MACross(bt.Strategy):
    # 設定參數
    params = (
        ('slow_period', 28),
        ('fast_period', 14),
        ('rsi_period', 14),
        ('long_side', 56),
        ('short_side', 44),
        ('stop_loss_pct', 4),
        ('retrace_stop_pct', 10)
    )

    def __init__(self):
        # 紀錄訂單信息
        self.order = None
        # 紀錄交易bar
        self.bar_executed = None
        # 開盤價
        self.dataopen = self.datas[0].open
        # 最高價
        self.datahigh = self.datas[0].high
        # 最低價
        self.datalow = self.datas[0].low
        # 收盤價
        self.dataclose = self.datas[0].close
        # 指標
        self.fastSMA = bt.ind.SMA(self.data.close, period=self.params.fast_period)
        self.slowSMA = bt.ind.SMA(self.data.close, period=self.params.slow_period)
        self.rsi = bt.ind.RSI(self.data.close, period=self.params.rsi_period)
        # 紀錄進出場價格
        self.entryLongPrice = None
        self.stopLongPrice = None
        self.retraceStopLongPrice = None

    def next(self):
        if self.order:
            return
        
        # 買入和賣出觸發條件（單個或多個）
        self.SMACrossover = self.CrossOver(self.fastSMA, self.slowSMA)
        self.enterLongCond1 = self.SMACrossover and (self.rsi[0] > self.params.long_side)
        self.SMACrossunder = self.CrossUnder(self.fastSMA, self.slowSMA)
        self.stopLongCond1 = self.SMACrossunder and (self.rsi[0] < self.params.short_side)
        
        # 無倉位
        if self.position.size == 0:
            # 做多
            if self.enterLongCond1:
                self.log(f'BUY, Price: {self.dataclose[0]}')
                self.stopLongPrice = self.dataclose[0] * (1 - (self.params.stop_loss_pct / 100))
                self.order = self.buy(exectype=bt.Order.Market)
        # 有倉位
        elif self.position.size > 0:
            # 設置回落停損點
            if (self.dataclose[0] > self.dataclose[-1]):
                self.retraceStopLongPrice = self.dataclose[0] * (1 - (self.params.retrace_stop_pct / 100))
                self.log(f'Sell, Price: {self.retraceStopLongPrice}')
                self.order = self.sell(price=self.retraceStopLongPrice, exectype=bt.Order.Stop, size=self.position.size, valid=timedelta(hours=1))
            # RSI條件觸發停損
            if self.stopLongCond1:
                self.log(f'Sell, Price: {self.dataclose[0]}')
                self.order = self.close(exectype=bt.Order.Market)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log('Order ACCEPTED/SUBMITTED', dt=order.created.dt)
            return
        
        if order.status in [order.Expired]:
            self.log('Order Expired')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'Buy Executed, Size: %d, Price: %.2f, Cost: %.2f, Commission: %.2f' %
                    (
                        order.executed.size,
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )           
            elif order.issell():
                self.log(
                    'Sell Executed, Size: %d, Price: %.2f, Cost: %.2f, Commission: %.2f' %
                    (
                        order.executed.size,
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )
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
    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            if isinstance(dt, float):
                dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    # 優化參數用
    def stop(self):
        print(self.params.slow_period, self.params.fast_period, self.params.rsi_period,
              self.params.long_side, self.params.short_side, self.params.stop_loss_pct, self.broker.getvalue())
        
    def CrossOver(self, a, b):
        return (a[0] > b[0], a[-1] <= b[-1])
    
    def CrossUnder(self, a, b):
        return (a[0] < b[0], a[-1] >= b[-1])