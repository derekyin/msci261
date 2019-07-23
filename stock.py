from datetime import datetime
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import numpy as np
class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.date = []
        self.closing_price = []
        _data = None

        _share = share.Share(self.ticker)
        try:
            _data = _share.get_historical(
                    share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1)
        except YahooFinanceError as e:
            print(e.message)
            sys.exit(1)

        for i in range (0, len(_data["timestamp"])):
            self.date.append(
                    datetime.fromtimestamp(int(_data["timestamp"][i])/1000))
            self.closing_price.append(_data["close"][i])

        self.returns = []
        for i in range(1, len(self.closing_price)):
            self.returns.append(
                    self.closing_price[i]/self.closing_price[i-1] - 1)
        self.mean = np.mean(self.get_returns())
        self.average = np.mean(self.get_returns())
        self.stddev = np.std(self.get_returns())
        self.var = np.var(self.get_returns())

    def get_returns(self):
        return self.returns
    
    def get_annual_return(self):
        return self.closing_price[-1] / self.closing_price[0] - 1

    def get_average(self):
        return self.average

    def get_var(self):
        return self.var

    def get_stddev(self):
        return self.stddev

class Portfolio:
    def __init__(self, stddev, var, avg_return, proportion):
        self.stddev = stddev
        self.var = var
        self.avg_return = avg_return
        self.proportion = proportion

    def __lt__(self, other):
        return self.var < other.var
    
    def __gt__(self, other):
        return self.var > other.var
