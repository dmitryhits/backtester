import backtrader as bt
import backtrader.indicators as bt_ind
import backtrader.talib as ta_ind


class CCI_Correction(bt.Strategy):
    params = dict(period_long=100, period_short=20)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        print('start init')
        # To keep track of pending orders
        self.order = None

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        self.cci_long = ta_ind.CCI(self.datas[0].high, self.datas[0].low, self.datas[0].close, timeperiod=self.p.period_long)
        print('cci long')
        self.cci_short = ta_ind.CCI(self.datas[0].high, self.datas[0].low, self.datas[0].close, timeperiod=self.p.period_short)
        print('cci short')

        self.Parabolic_SAR = ta_ind.SAR(self.datas[0].high, self.datas[0].low)
        self.bull_zone = False
        self.bearish_pull_back = False
        self.bullish_pull_back = False



    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # print('next')
        if self.cci_long > 100:
            self.bull_zone = True
            print('Bull Zone')
        if self.cci_long < -100:
            self.bull_zone = False
            print('Bear Zone')
        if self.bull_zone and self.cci_short < -100:
            self.bullish_pull_back = True
            self.bearish_pull_back = False
            print('Bullish Pullback')
        if (not self.bull_zone) and self.cci_short > 100:
            self.bearish_pull_back = True
            self.bullish_pull_back = False
            print('Bearish Pullback')
        if self.bullish_pull_back and self.cci_short > 0:
            self.order = self.buy()
        if self.bearish_pull_back and self.cci_short < 0:
            self.order = self.sell()
        if self.position:
            if (self.bull_zone and self.Parabolic_SAR > self.datas[0].high) or \
                    ((not self.bull_zone) and self.Parabolic_SAR < self.datas[0].low):
                self.order = self.close()


if __name__ == '__main__':

    import pandas as pd
    import os
    import datetime
    import sys

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(CCI_Correction)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    data_path = '/Users/hits/DropboxPersonal/notebooks/data/'
    data_file = 'AAPL_1day.h5'
    path = os.path.join(data_file+data_path)

    # Create a Data Feed
    all_data = pd.read_hdf(data_path + data_file)
    all_data = all_data.sort_index()
    data2006 = all_data["2006"]
    #print(data2006.head())
    #print(data2006.tail())
    bt_data = bt.feeds.PandasData(dataname=data2006)

    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data)

    # Set our desired cash start
    cerebro.broker.setcash(1000000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100000)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


