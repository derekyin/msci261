import numpy as np
import stock

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
        portfolio_avg_return = np.mean(portfolio_return)

        portfolios.append(stock.Portfolio(portfolio_stddev, portfolio_var, portfolio_avg_return, i))

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

if __name__ == '__main__':
    main()
