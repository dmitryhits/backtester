import backtrader as bt
import backtrader.indicators as bt_ind
import backtrader.talib as ta_ind


class CCI_Correction(bt.Strategy):
    params = dict(period_long=100, period_short=20)

    def __init__(self):
        print('start init')
        self.cci_long = ta_ind.CCI([self.data.high, self.data.low, self.data.close], timeperiod=self.p.period_long)
        print('cci long')
        self.cci_short = ta_ind.CCI([self.data.high, self.data.low, self.data.close], timeperiod=self.p.period_short)
        print('cci short')
        self.bull_zone = False
        self.bear_zone = False
        self.bearish_pull_back = False
        self.bullish_pull_back = False

    def next(self):
        print('next')
        if self.cci_long > 100:
            self.bull_zone = True
            print('Bull Zone')
        if self.cci_long < -100:
            self.bear_zone = True
            print('Bear Zone')
        if self.bull_zone and self.cci_short < -100:
            self.bullish_pull_back = True
            print('Bullish Pullback')
        if self.bear_zone and self.cci_short > 100:
            self.bearish_pull_back = True
            print('Bearish Pullback')
        if self.bullish_pull_back and self.cci_short > 0:
            self.buy(size=1e5//self.self.data.close)
        if self.bearish_pull_back and self.cci_short < 0:
            self.sell(size=1e5//self.self.data.close)
        if self.position:
            if (self.bull_zone and ta_ind.SAR([self.data.high, self.data.low]) > self.data.high) or \
                    (self.bear_zone and ta_ind.SAR([self.data.high, self.data.low]) < self.data.low):
                self.close()


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
    #data2006 = all_data["2006"]
    #print(data2006.head())
    #print(data2006.tail())
    bt_data = bt.feeds.PandasData(dataname=all_data)

    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data)

    # Set our desired cash start
    cerebro.broker.setcash(1000000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


