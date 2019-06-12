import backtrader as bt
import datetime
import os.path
import sys
import pandas as pd


class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('bol_period', 20),
        ('bol_dev_factor', 2),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        print("Running?")
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders
        self.order = None

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
        # Add Bollinger Bands Percentage Indicator
        self.bbandpct = bt.indicators.BollingerBandsPct(
        self.datas[0], period=self.params.bol_period, devfactor=self.params.bol_dev_factor)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0], plot = False)
        bt.indicators.MACDHisto(self.datas[0], plot = False)
        rsi = bt.indicators.RSI(self.datas[0], plot = False)
        bt.indicators.SmoothedMovingAverage(rsi, period=10, plot=False)
        bt.indicators.ATR(self.datas[0], plot=False)
        bt.indicators.BollingerBandsPct(self.datas[0],
                                        period=self.params.bol_period,
                                        devfactor = self.params.bol_dev_factor,
                                        plot=True, subplot=True)

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

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.bbandpct>.8:
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if self.bbandpct<.2:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MyStrategy)

    data_path = '/Users/hits/DropboxPersonal/notebooks/data/'
    data_file = 'AAPL_1day.h5'
    path = os.path.join(data_file + data_path)

    # Create a Data Feed
    all_data = pd.read_hdf(data_path + data_file)
    all_data = all_data.sort_index()
    data2006 = all_data["2006"]
    #print(all_data.head())
    #print(all_data.tail())
    bt_data = bt.feeds.PandasData(dataname=data2006)

    cerebro.adddata(bt_data)

    # Set our desired cash start
    cerebro.broker.setcash(1000000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100000)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())