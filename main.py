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


    def __init__(self, stock_A, stock_B, risk_free_rate, allow_short=False):
        profits = [stock_A.get_returns(), stock_B.get_returns()]
        x = np.ones(len(profits))
        mean_vector = [stock_A.get_annual_return(), stock_B.get_annual_return()]
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
    if not ticker_a:
        ticker_a = input("Enter stock ticker A\n")
    if not ticker_b:
        ticker_b = input("Enter stock ticker B\n")

    stock_A = stock.Stock(ticker_a)
    stock_B = stock.Stock(ticker_b)

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
        portfolio_avg_return = stock_A.get_annual_return() * i * 0.025 + stock_B.get_annual_return() * (1 - i * 0.025)

#        print("{},{}".format(portfolio_avg_return, portfolio_stddev))
        portfolios.append(stock.Portfolio(portfolio_stddev, portfolio_var, portfolio_avg_return, i * 0.025))

    min_portfolio = min(portfolios)

    print()
    print("MVP proportion {} {}".format(stock_A.ticker, min_portfolio.proportion))
    print("MVP proportion {} {}".format(stock_B.ticker, 1 - min_portfolio.proportion))
    print("MVP standard deviation {}".format(min_portfolio.stddev))
    print("MVP expected portfolio return {}".format(min_portfolio.avg_return))

    sharpe = sharpe_optimizer(stock_A, stock_B, 0.02)

    print()
    print("Case 1:")
    print("Proportion in risk free: 0%")
    print("Proportion in market portfolio: 100%")
    print("Maximum Sharpe Ratio: {}".format(sharpe.sharpe))
    print("Market portfolio proportion {}: {}%".format(stock_A.ticker, sharpe.result.x[0] * 100))
    print("Market portfolio proportion {}: {}%".format(stock_B.ticker, sharpe.result.x[1] * 100))
    print("Market portfolio expected return: {}%".format(sharpe.avg_return * 100))
    print("Market portfolio standard deviation: {}%".format(sharpe.stddev * 100))

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

if __name__ == '__main__':
    main()
