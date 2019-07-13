from datetime import datetime
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import numpy as np
import stock

ticker_a = input("Enter stock ticker A\n")
ticker_b = input("Enter stock ticker B\n")

stock_a = share.Share(ticker_a)
stock_b = share.Share(ticker_b)

a_data = None
b_data = None

try:
    a_data = stock_a.get_historical(share.PERIOD_TYPE_YEAR,1, share.FREQUENCY_TYPE_DAY, 1)
except YahooFinanceError as e:
    print(e.message)
    sys.exit(1)

try:
    b_data = stock_b.get_historical(share.PERIOD_TYPE_YEAR,1, share.FREQUENCY_TYPE_DAY, 1)
except YahooFinanceError as e:
    print(e.message)
    sys.exit(1)

stock_A = stock.Stock(ticker_a)
stock_B = stock.Stock(ticker_b)

for i in range (0, len(a_data["timestamp"])):
    stock_A.date.append(datetime.fromtimestamp(int(a_data["timestamp"][i])/1000))
    stock_A.closing_price.append(a_data["close"][i])

for i in range (0, len(b_data["timestamp"])):
    stock_B.date.append(datetime.fromtimestamp(int(b_data["timestamp"][i])/1000))
    stock_B.closing_price.append(b_data["close"][i])

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
print("MVP expected porfolio return {}".format(min_portfolio.avg_return))