import numpy as np
# import stock
from datetime import datetime
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import numpy as np
from flask import Flask, request, jsonify

def get(request):
    request_json = request.get_json()

    stock_a = request_json['a']
    stock_b = request_json['b']

    if stock_a and stock_b:
        return jsonify(main(stock_a.strip(), stock_b.strip()))
    return jsonify({})

def main(ticker_a=None, ticker_b=None):
    if not ticker_a:
        ticker_a = input("Enter stock ticker A\n")
    if not ticker_b:
        ticker_b = input("Enter stock ticker B\n")

    stock_A = Stock(ticker_a)
    stock_B = Stock(ticker_b)

    print("----{}----".format(stock_A.ticker))
    print("mean return of {}: ".format(stock_A.ticker), stock_A.get_average()) 
    print("s.d of {}: ".format(stock_A.ticker), stock_A.get_stddev()) 
    print("variance of {}: ".format(stock_A.ticker), stock_A.get_var())

    print("----{}----".format(stock_B.ticker))
    print("mean return of {}: ".format(stock_B.ticker), stock_B.get_average()) 
    print("s.d of {}: ".format(stock_B.ticker), stock_B.get_stddev()) 
    print("variance of {}: ".format(stock_B.ticker), stock_B.get_var())

    portfolios = []
    for i in range(0, 41):
        portfolio_return = [ stock_A.get_returns()[j] * i * 0.025 + stock_B.get_returns()[j] * (1 - i * 0.025) for j in range(0, len(stock_A.get_returns())) ]
        portfolio_stddev = np.std(portfolio_return)
        portfolio_var = np.var(portfolio_return)
        portfolio_avg_return = np.mean(portfolio_return)

        portfolios.append(Portfolio(portfolio_stddev, portfolio_var, portfolio_avg_return, i))

    min_portfolio = min(portfolios)

    print()
    print("MVP proportion {} {}".format(stock_A.ticker, min_portfolio.proportion))
    print("MVP proportion {} {}".format(stock_B.ticker, 1 - min_portfolio.proportion))
    print("MVP standard deviation {}".format(min_portfolio.stddev))
    print("MVP expected portfolio return {}".format(min_portfolio.avg_return))

    return {
            "stock_a": {
                "ticker": ticker_a,
                "mean": stock_A.get_average(),
                "sd": stock_A.get_stddev()
            },
            "stock_b": {
                "ticker": ticker_b,
                "mean": stock_B.get_average(),
                "sd": stock_B.get_stddev()
            },
            "mvp":{
                "prop_a": min_portfolio.proportion,
                "prop_b": 1-min_portfolio.proportion,
                "return": min_portfolio.avg_return,
                "sd": min_portfolio.stddev
            }
        }

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
        self.proportion = proportion * 0.025

    def __lt__(self, other):
        return self.var < other.var
    
    def __gt__(self, other):
        return self.var > other.var


if __name__ == '__main__':
    main()
