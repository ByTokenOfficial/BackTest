import backtrader as bt


# Define your strategy
class NewStrategy(bt.Strategy):
    # 設定參數
    params = (
        ('param1', 1),
        ('param2', 2)
    )

    def __init__(self):
        # 紀錄訂單信息
        self.order = None
        # 紀錄交易bar
        self.bar_executed = None
        # 用開盤價做交易
        self.dataopen = self.datas[0].open
        # 最高價
        self.datahigh = self.datas[0].high
        # 最低價
        self.datalow = self.datas[0].low
        # 收盤價
        self.dataclose = self.datas[0].close

    def next(self):
        # 打印每日收盤價
        # self.log(f'Close: {self.dataclose[0]}')
        # 買入和賣出觸發條件（單個或多個）
        self.cond1 = (self.kd.lines.k[-1] < self.kd.lines.d[-1]) and (self.kd.lines.k[0] > self.kd.lines.d[0])
        self.cond2 = True

        if self.order:
            return 
        # 帳戶沒有部位
        if not self.position:
            # 進場條件
            if self.cond1:
                self.log('BUY ' + ', Price: ' + str(self.dataclose[0]))
                # 使用開盤價買入標的
                self.order = self.buy(price=self.dataclose[0])
        # 有部位，賣出條件
        else:
            if self.cond2:
                # 印出買賣日期與價位
                self.log('SELL ' + ', Price: ' + str(self.dataclose[0]))
                # 使用下一根開盤價賣出標的
                self.order = self.close(price=self.dataclose[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log('Order ACCEPTED/SUBMITTED', dt=order.create.dt)
            self.order = order
            return
        
        if order.status in [order.Expired]:
            self.log('Buy Expired')

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
        print(self.params.params1, self.params.params2,
              self.broker.getvalue())