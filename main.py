import logging
from typing import List
import numpy as np
from scipy import optimize
import stock

class sharpe_optimizer:
    def __stddev(self, x, cov_matrix):
        return np.sqrt(x.dot(cov_matrix).dot(x.T))


    def __target_func(self, x, cov_matrix, mean_vector, risk_free_rate):
        # maximize by minimizing the negative version
        f = float(-(x.dot(mean_vector) - risk_free_rate) / self.__stddev(x, cov_matrix))
        return f


    def __init__(self, stocks : List[stock.Stock], risk_free_rate, allow_short=False):
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
        self.result = optimize.minimize(self.__target_func, x, args=(cov_matrix, mean_vector, risk_free_rate,), bounds=bounds,
                                     constraints=cons)
        self.sharpe = -self.__target_func(self.result.x, cov_matrix, mean_vector, risk_free_rate)
        self.stddev = self.__stddev(self.result.x, cov_matrix)
        self.avg_return = self.result.x.dot(mean_vector)


def main(ticker_a=None, ticker_b=None):
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")

    if not ticker_a:
        ticker_a = input("Enter stock ticker A\n")
    if not ticker_b:
        ticker_b = input("Enter stock ticker B\n")

    stock_A = stock.Stock(ticker_a)
    stock_B = stock.Stock(ticker_b)

    logger.info("----{}----".format(stock_A.ticker))
    logger.info("mean return of {}: {}".format(stock_A.ticker, stock_A.get_annual_return()))
    logger.info("s.d of {}: {}".format(stock_A.ticker, stock_A.get_stddev()))
    logger.info("variance of {}: {}".format(stock_A.ticker, stock_A.get_var()))

    logger.info("----{}----".format(stock_B.ticker))
    logger.info("mean return of {}: {}".format(stock_B.ticker, stock_B.get_annual_return()))
    logger.info("s.d of {}: {}".format(stock_B.ticker, stock_B.get_stddev()))
    logger.info("variance of {}: {}".format(stock_B.ticker, stock_B.get_var()))

    portfolios = []
    for i in range(0, 41):
        portfolio_return = [ stock_A.get_returns()[j] * i * 0.025 + stock_B.get_returns()[j] * (1 - i * 0.025) for j in range(0, len(stock_A.get_returns())) ]
        portfolio_stddev = np.std(portfolio_return)
        portfolio_var = np.var(portfolio_return)
        portfolio_avg_return = stock_A.get_annual_return() * i * 0.025 + stock_B.get_annual_return() * (1 - i * 0.025)

#        print("{},{}".format(portfolio_avg_return, portfolio_stddev))
        portfolios.append(stock.Portfolio(portfolio_stddev, portfolio_var, portfolio_avg_return, i * 0.025))

    min_portfolio = min(portfolios)

    logger.info("")
    logger.info("MVP proportion {} {}".format(stock_A.ticker, min_portfolio.proportion))
    logger.info("MVP proportion {} {}".format(stock_B.ticker, 1 - min_portfolio.proportion))
    logger.info("MVP standard deviation {}".format(min_portfolio.stddev))
    logger.info("MVP expected portfolio return {}".format(min_portfolio.avg_return))

    sharpe = sharpe_optimizer([stock_A, stock_B], 0.02)

    logger.info("")
    logger.info("Case 1:")
    logger.info("Proportion in risk free: 0%")
    logger.info("Proportion in market portfolio: 100%")
    logger.info("Maximum Sharpe Ratio: {}".format(sharpe.sharpe))
    logger.info("Market portfolio proportion {}: {}%".format(stock_A.ticker, sharpe.result.x[0] * 100))
    logger.info("Market portfolio proportion {}: {}%".format(stock_B.ticker, sharpe.result.x[1] * 100))
    logger.info("Market portfolio expected return: {}%".format(sharpe.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(sharpe.stddev * 100))

    case2 = stock.Portfolio(0.5 * sharpe.stddev, 0.5**2 * sharpe.stddev**2, 0.5 * (0.02 + sharpe.avg_return), 0.5)
    case3 = stock.Portfolio(1.5 * sharpe.stddev, 1.5**2 * sharpe.stddev**2, -0.5 * 0.02 + 1.5 * sharpe.avg_return, -0.5)

    logger.info("")
    logger.info("Case 2:")
    logger.info("Proportion in risk free: 50%")
    logger.info("Proportion in market portfolio: 50%")
    logger.info("Market portfolio expected return: {}%".format(case2.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(case2.stddev * 100))

    logger.info("")
    logger.info("Case 3:")
    logger.info("Proportion in risk free: -50%")
    logger.info("Proportion in market portfolio: 150%")
    logger.info("Market portfolio expected return: {}%".format(case3.avg_return * 100))
    logger.info("Market portfolio standard deviation: {}%".format(case3.stddev * 100))


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
            "mvp": {
                "prop_a": min_portfolio.proportion,
                "prop_b": 1-min_portfolio.proportion,
                "return": min_portfolio.avg_return,
                "sd": min_portfolio.stddev
            },
            "cml": [
                {
                    "prop_rf": -0.5,
                    "prop_market": 1.5,
                    "annual_return": case3.avg_return,
                    "sd": case3.stddev
                },
                {
                    "prop_rf": 0.5,
                    "prop_market": 0.5,
                    "annual_return": case2.avg_return,
                    "sd": case2.stddev
                },
                {
                    "prop_rf": 0,
                    "prop_market": 1,
                    "sharpe": sharpe.sharpe,
                    "market": sharpe.result.x.tolist(),
                    "annual_return": sharpe.avg_return,
                    "sd": sharpe.stddev
                }
            ]
        }

if __name__ == '__main__':
    main()
