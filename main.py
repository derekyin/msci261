from copy import copy
from datetime import datetime
from flask import request, jsonify
from random import random
from scipy import optimize
from typing import List
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import logging
import numpy as np
import sys


def get(request):
    request_json = request.get_json()

    stock_a = request_json['a']
    stock_b = request_json['b']

    if stock_a and stock_b:
        return jsonify(main(stock_a.strip(), stock_b.strip()))
    return jsonify({})


def stddev(x, cov_matrix):
    return np.sqrt(x.dot(cov_matrix).dot(x.T))


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.closing_price = []
        _data = None

        _share = share.Share(self.ticker)
        _data = _share.get_historical(
            share.PERIOD_TYPE_YEAR, 2, share.FREQUENCY_TYPE_DAY, 1)
        if not _data:
            raise ValueError("No data on stock {}".format(ticker))

        for i in range(0, len(_data["timestamp"])):
            date = datetime.fromtimestamp(int(_data["timestamp"][i])/1000)
            if date >= datetime(2018, 6, 1) and date < datetime(2019, 6, 1):
                self.closing_price.append(_data["close"][i])

        self.returns = []
        for i in range(1, len(self.closing_price)):
            if not self.closing_price[i] or not self.closing_price[i-1]:
                self.returns.append(0)
            else:
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
    def combine(cls, proportions: np.ndarray, stocks: List):
        combined = copy(stocks[0])
        combined.ticker = "portfolio " + \
            " ".join([stock.ticker for stock in stocks])
        combined.closing_price = []
        combined.returns = []

        for i in range(len(stocks[0].closing_price)):
            combined.closing_price.append(proportions.dot(
                [stock.closing_price[i] for stock in stocks]))

        for i in range(len(stocks[0].returns)):
            combined.returns.append(proportions.dot(
                [stock.returns[i] for stock in stocks]))

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
    def __init__(self, proportions: np.ndarray, stocks: List[Stock]):
        self.proportions = proportions
        self.stocks = stocks
        self.cov_matrix = np.cov([stock.get_returns() for stock in stocks])
        self.stddev = stddev(self.proportions, self.cov_matrix)
        self.var = self.stddev**2
        self.avg_return = proportions.dot(
            [stock.get_annual_return() for stock in stocks])

    def __lt__(self, other):
        return self.var < other.var

    def __gt__(self, other):
        return self.var > other.var


class sharpe_optimizer:
    def __sharpe_ratio(self, x, cov_matrix, mean_vector, risk_free_rate):
        # maximize by minimizing the negative version
        f = float(-(x.dot(mean_vector) - risk_free_rate) /
                  stddev(x, cov_matrix))
        return f

    def __init__(self, stocks: List[Stock], risk_free_rate, allow_short=False):
        profits = [stock.get_returns() for stock in stocks]
        x = np.ones(len(profits))
        mean_vector = [stock.get_annual_return() for stock in stocks]
        cov_matrix = np.cov(profits)
        cons = ({'type': 'eq',
                 'fun': lambda x: np.sum(x) - 1})
        if not allow_short:
            bounds = [(0, None,) for i in range(len(x))]
        else:
            bounds = None
        self.result = optimize.minimize(self.__sharpe_ratio, x, args=(cov_matrix, mean_vector, risk_free_rate,), bounds=bounds,
                                        constraints=cons)
        self.sharpe = - \
            self.__sharpe_ratio(self.result.x, cov_matrix,
                                mean_vector, risk_free_rate)
        self.stddev = stddev(self.result.x, cov_matrix)
        self.avg_return = self.result.x.dot(mean_vector)


class mvp_optimizer:
    def __init__(self, stocks: List[Stock]):
        profits = [stock.get_returns() for stock in stocks]
        x = np.ones(len(profits))
        mean_vector = [stock.get_annual_return() for stock in stocks]
        cov_matrix = np.cov(profits)
        cons = ({'type': 'eq',
                 'fun': lambda x: np.sum(x) - 1})
        bounds = [(0, 1) for i in range(len(x))]
        self.result = optimize.minimize(stddev, x, args=(cov_matrix), bounds=bounds,
                                        constraints=cons)


def find_random_portfolio(_):
    all_tickers = [
        "AN",
        "BFRA",
        "BFS",
        "CACC",
        "CNA",
        "CRMD",
        "CTAS",
        "DGL",
        "ENLV",
        "EWRE",
        "FBIO",
        "FEIM",
        "FLDM",
        "FLGR",
        "FLR",
        "FMAT",
        "GSHD",
        "HASI",
        "HFBL",
        "HJV",
        "HK",
        "HOLD",
        "IFGL",
        "INFI",
        "JASN",
        "JHX",
        "JJE",
        "LQDI",
        "NIB",
        "RBUS",
        "RVRS",
        "RYJ",
        "SHOS",
        "UEIC",
        "UTI",
        "UUU",
        "VCYT",
        "VFLQ",
        "VNQ",
        "VO",
        "WLKP",
        "WPM",
        "XTH",
    ]

    random_stocks = []
    random_tickers = []
    random_portfolio = None
    found = False
    while not found:
        random_tickers = []
        random_stocks = []
        n_period = None
        while len(random_stocks) < 10:
            try:
                _stock = Stock(
                    all_tickers[int(len(all_tickers) * random())])
            except:
                continue
            if _stock.ticker in random_tickers:
                continue
            elif not n_period:
                n_period = len(_stock.returns)
            elif n_period != len(_stock.returns):
                continue
            random_stocks.append(_stock)
            random_tickers.append(_stock.ticker)
            if len(random_stocks) > 4:
                _proportions = np.array(
                    [1/len(random_stocks)] * len(random_stocks))
                random_portfolio = Portfolio(_proportions, random_stocks)
                if random_portfolio.stddev < 0.05 and random_portfolio.avg_return > 0.1:
                    found = True
                    break
    return jsonify({
        "stocks": [{
            "ticker": s.ticker,
            "annual_return": s.get_annual_return(),
            "sd": s.get_stddev()
            } for s in random_portfolio.stocks],
        "proportions": random_portfolio.proportions.tolist(),
        "annual_return": random_portfolio.avg_return,
        "stddev": random_portfolio.stddev
    })


def main(ticker_a=None, ticker_b=None):
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")

    if not ticker_a:
        ticker_a = input("Enter stock ticker A\n")
    if not ticker_b:
        ticker_b = input("Enter stock ticker B\n")

    try:
        stock_A = Stock(ticker_a)
        stock_B = Stock(ticker_b)
    except YahooFinanceError as e:
        return {
            "error": e.message
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

    if len(stock_A.returns) != len(stock_B.returns):
        return {
            "error": "{} and {} cannot be compared. Different trading dates.".format(ticker_a, ticker_b)
        }

    logger.info("----{}----".format(stock_A.ticker))
    logger.info("mean return of {}: {}".format(
        stock_A.ticker, stock_A.get_annual_return()))
    logger.info("s.d of {}: {}".format(stock_A.ticker, stock_A.get_stddev()))
    logger.info("variance of {}: {}".format(stock_A.ticker, stock_A.get_var()))

    logger.info("----{}----".format(stock_B.ticker))
    logger.info("mean return of {}: {}".format(
        stock_B.ticker, stock_B.get_annual_return()))
    logger.info("s.d of {}: {}".format(stock_B.ticker, stock_B.get_stddev()))
    logger.info("variance of {}: {}".format(stock_B.ticker, stock_B.get_var()))

    mvp = mvp_optimizer([stock_A, stock_B])
    min_portfolio = Portfolio(mvp.result.x, [stock_A, stock_B])

    logger.info("")
    logger.info("MVP proportion {} {}".format(
        stock_A.ticker, min_portfolio.proportions[0]))
    logger.info("MVP proportion {} {}".format(
        stock_B.ticker, min_portfolio.proportions[1]))
    logger.info("MVP standard deviation {}".format(min_portfolio.stddev))
    logger.info("MVP expected portfolio return {}".format(
        min_portfolio.avg_return))

    sharpe = sharpe_optimizer([stock_A, stock_B], 0.02)

    logger.info("")
    logger.info("Case 1:")
    logger.info("Proportion in risk free: 0%")
    logger.info("Proportion in market portfolio: 100%")
    logger.info("Maximum Sharpe Ratio: {}".format(sharpe.sharpe))
    logger.info("Market portfolio proportion {}: {}%".format(
        stock_A.ticker, sharpe.result.x[0] * 100))
    logger.info("Market portfolio proportion {}: {}%".format(
        stock_B.ticker, sharpe.result.x[1] * 100))
    logger.info("Market portfolio expected return: {}%".format(
        sharpe.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(
        sharpe.stddev * 100))

    rf = Stock.risk_free(0.02, stock_A)
    market_portfolio = Stock.combine(sharpe.result.x, [stock_A, stock_B])
    case2 = Portfolio(np.array([0.5, 0.5]), [rf, market_portfolio])
    case3 = Portfolio(np.array([-0.5, 1.5]), [rf, market_portfolio])

    logger.info("")
    logger.info("Case 2:")
    logger.info("Proportion in risk free: 50%")
    logger.info("Proportion in market portfolio: 50%")
    logger.info("Market portfolio expected return: {}%".format(
        case2.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(
        case2.stddev * 100))

    logger.info("")
    logger.info("Case 3:")
    logger.info("Proportion in risk free: -50%")
    logger.info("Proportion in market portfolio: 150%")
    logger.info("Market portfolio expected return: {}%".format(
        case3.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(
        case3.stddev * 100))

    return {
        "stocks": [
            {
                "ticker": ticker_a,
                "mean_daily": stock_A.get_average(),
                "mean_annual": stock_A.get_annual_return(),
                "sd": stock_A.get_stddev()
            },
            {
                "ticker": ticker_b,
                "mean_daily": stock_B.get_average(),
                "mean_annual": stock_B.get_annual_return(),
                "sd": stock_B.get_stddev()
            }
        ],
        "cov": np.cov([stock_A.get_returns(), stock_B.get_returns()]).tolist()[0][1],
        "mvp": {
            "prop_a": min_portfolio.proportions[0],
            "prop_b": min_portfolio.proportions[1],
            "return": min_portfolio.avg_return,
            "sd": min_portfolio.stddev
        },
        "cml": [
            {
                "prop_rf": 0,
                "prop_market": 1,
                "sharpe": sharpe.sharpe,
                "market": sharpe.result.x.tolist(),
                "annual_return": sharpe.avg_return,
                "sd": sharpe.stddev
            },
            {
                "prop_rf": 0.5,
                "prop_market": 0.5,
                "annual_return": case2.avg_return,
                "sd": case2.stddev
            },
            {
                "prop_rf": -0.5,
                "prop_market": 1.5,
                "annual_return": case3.avg_return,
                "sd": case3.stddev
            }
        ]
    }


if __name__ == '__main__':
    main()
