from copy import copy
from datetime import datetime
from typing import List
from yahoo_finance_api2 import share
import logging
import numpy as np
import sys

def stddev(x, cov_matrix):
    return np.sqrt(x.dot(cov_matrix).dot(x.T))


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.date = []
        self.closing_price = []
        _data = None

        _share = share.Share(self.ticker)
        _data = _share.get_historical(
                share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1)
        if not _data:
            raise ValueError("No data on stock {}".format(ticker))

        for i in range (0, len(_data["timestamp"])):
            self.date.append(
                    datetime.fromtimestamp(int(_data["timestamp"][i])/1000))
            self.closing_price.append(_data["close"][i])

        self.returns = []
        for i in range(1, len(self.closing_price)):
            self.returns.append(
                    self.closing_price[i]/self.closing_price[i-1] - 1)

        self.average = np.mean(self.get_returns())
        self.stddev = np.std(self.get_returns())
        self.var = np.var(self.get_returns())

    def get_returns(self):
        return self.returns
    
    def get_annual_return(self):
        return (1 + self.get_average()) ** len(self.get_returns()) - 1

    def get_average(self):
        return self.average

    def get_var(self):
        return self.var

    def get_stddev(self):
        return self.stddev

    @classmethod
    def combine(cls, proportions : np.ndarray, stocks : List):
        combined = copy(stocks[0])
        combined.ticker = "portfolio " + " ".join([stock.ticker for stock in stocks])
        combined.closing_price = []
        combined.returns = []

        for i in range(len(stocks[0].closing_price)):
            combined.closing_price.append(proportions.dot([stock.closing_price[i] for stock in stocks]))

        for i in range(len(stocks[0].returns)):
            combined.returns.append(proportions.dot([stock.returns[i] for stock in stocks]))

        combined.average = np.mean(combined.get_returns())

        tmp = Portfolio(proportions, stocks)
        combined.stddev = tmp.stddev
        combined.var = tmp.var
        return combined


    @classmethod
    def risk_free(cls, rate, other):
        rf = copy(other)
        rf.ticker = "risk free " + str(rate)
        rf.closing_price = []
        rf.average = (1 + rate)**(1/len(other.returns)) - 1
        rf.returns = [rf.average for i in other.returns]
        rf.stddev = 0
        rf.var = 0
        return rf

class Portfolio:
    def __init__(self, proportions : np.ndarray, stocks : List[Stock]):
        self.proportions = proportions
        self.stocks = stocks
        self.cov_matrix = np.cov([stock.get_returns() for stock in stocks])
        self.stddev = stddev(self.proportions, self.cov_matrix)
        self.var = self.stddev**2
        self.avg_return = proportions.dot([stock.get_annual_return() for stock in stocks])

    def __lt__(self, other):
        return self.var < other.var
    
    def __gt__(self, other):
        return self.var > other.var
