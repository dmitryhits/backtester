import backtrader as bt
import backtrader.indicators as bt_ind
import backtrader.talib as ta_ind
from backtrader.indicators import psar
import numpy as np


# class ParabolicSAR(psar.ParabolicSAR):
#     lines = ('psar',)
#     params = (
#         ('period', 2),  # when to start showing values
#         ('af', 0.02),
#         ('afmax', 0.20),
#     )
#     plotlines = {'psar': dict(
#         marker='.', color='blue',
#         markersize=4.0, fillstyle='full', ls='')
#     }


class FlexSizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        stake = cash//data-100
        # print("stake", stake, "cash", cash)
        return stake


class CCI_Correction(bt.Strategy):
    params = dict(period_long=100, period_short=20, sar_period=2, sar_af=0.015, sar_afmax=0.05)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # print('start init')
        # To keep track of pending orders
        self.order = None

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.data.close

        self.cci_long = ta_ind.CCI(self.data.high, self.data.low, self.data.close, timeperiod=self.p.period_long)
        # print('cci long')
        self.cci_short = ta_ind.CCI(self.data.high, self.data.low, self.data.close, timeperiod=self.p.period_short)
        # print('cci short')

        self.Parabolic_SAR = psar.ParabolicSAR(self.data,
                                               period=self.p.sar_period, af=self.p.sar_af, afmax=self.p.sar_afmax)
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
                pass
                #self.log('BUY EXECUTED, %.2f' % order.executed.price)

            elif order.issell():
                pass
                #self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.status is order.Canceled:
                self.log('Order Canceled')
            if order.status is order.Margin:
                pass
                # self.log('Order Margin')
            if order.status is order.Rejected:
                self.log('Order Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # print('next')
        if self.cci_long[0] > 100:
            self.bull_zone = True
            # print('Bull Zone')
        if self.cci_long[0] < -100:
            self.bull_zone = False
            #print('Bear Zone')
        if self.bull_zone and self.cci_short[0] < -100:
            self.bullish_pull_back = True
            self.bearish_pull_back = False
            # print('Bullish Pullback')
        if (not self.bull_zone) and self.cci_short[0] > 100:
            self.bearish_pull_back = True
            self.bullish_pull_back = False
            # print('Bearish Pullback')
        if self.bullish_pull_back and self.cci_short[0] > 0:
            self.order = self.buy()
            self.bullish_pull_back =False
            # print('CCI short {0:.0f}, CCI_long {1:.0f}'.format(self.cci_short[0], self.cci_long[0]))
        if self.bearish_pull_back and self.cci_short[0] < 0:
            self.order = self.sell()
            self.bearish_pull_back = False
        if self.position:
            if (self.bull_zone and self.Parabolic_SAR[0] > self.datas[0].high) or \
                    ((not self.bull_zone) and self.Parabolic_SAR[0] < self.datas[0].low):
                self.order = self.close()

    def stop(self):
        self.log('(SAR AF MAX %.3f) (SAR AF %.3f) Ending Value %.2f' %
                 (self.p.sar_afmax, self.p.sar_af, self.broker.getvalue()))


if __name__ == '__main__':

    import pandas as pd
    import os
    import datetime
    import sys

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(CCI_Correction)

    # Optimize a strategy
    # strats = cerebro.optstrategy(
    #     CCI_Correction,
    #     sar_afmax=np.arange(0.01, 0.2, 0.01),
    #     sar_af=np.arange(0.001, 0.02, 0.001),
    # )

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    data_path = '/Users/hits/DropboxPersonal/notebooks/data/'
    data_file = 'AAPL_1day.h5'
    path = os.path.join(data_file+data_path)

    # Create a Data Feed
    all_data = pd.read_hdf(data_path + data_file)
    all_data = all_data.sort_index()
    # Adjust for splits
    price_data = ['Open', 'High', 'Low', 'Close', 'WAP']
    split_dates = ['2000-6-20', '2005-2-27', '1987-6-15']
    all_data.loc[:'2000-6-20', price_data] = all_data.loc[:'2000-6-20', price_data]/2
    all_data.loc[:'2005-2-27', price_data] = all_data.loc[:'2005-2-27', price_data]/2
    all_data.loc[:'1987-6-15', price_data] = all_data.loc[:'1987-6-15', price_data]/2
    # correct wrong data
    all_data.loc['2007-11-30', 'Low'] = 25.67

    partial_data = all_data["2005":"2007"]
    #print(data2006.head())
    #print(data2006.tail())
    bt_data = bt.feeds.PandasData(dataname=partial_data)

    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data)

    # Set our desired cash start
    cerebro.broker.setcash(1000000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(FlexSizer, stake=100)

    # Print out the starting conditions
    # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run(maxcpus=1)

    # # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()



