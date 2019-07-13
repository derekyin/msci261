import numpy as np
class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.date = []
        self.closing_price = []

    def get_returns(self):
        returns = []
        for i in range(1, len(self.closing_price)):
            returns.append(self.closing_price[i]/self.closing_price[i-1] - 1)

        return returns
    
    def get_average(self):
        return np.mean(self.get_returns())

    def get_var(self):
        return np.var(self.get_returns())

    def get_stddev(self):
        return np.std(self.get_returns())

class Portfolio:
    def __init__(self, stddev, var, avg_return, proportion):
        self.stddev = stddev
        self.var = var
        self.avg_return = avg_return
        self.proportion = proportion * 0.025

    def __lt__(self, other):
        return self.var < other.var
    
    def __gt__(self, other):
        return self.var > other.var