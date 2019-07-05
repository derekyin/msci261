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
    stock_A.date.append(datetime.fromtimestamp(int(str(a_data["timestamp"][i])[:-3])))
    stock_A.closing_price.append(a_data["close"][i])

for i in range (0, len(b_data["timestamp"])):
    stock_B.date.append(datetime.fromtimestamp(int(str(b_data["timestamp"][i])[:-3])))
    stock_B.closing_price.append(b_data["close"][i])

print("----{}----".format(stock_A.ticker))
a_mean = np.mean(stock_A.closing_price)
print("mean of {}: ".format(stock_A.ticker), np.mean(stock_A.closing_price)) 
print("s.d of {}: ".format(stock_A.ticker), np.std(stock_A.closing_price)) 
print("variance of {}: ".format(stock_A.ticker), np.var(stock_A.closing_price))

print("----{}----".format(ticker_b))
b_mean = np.mean(stock_B.closing_price)
print("mean of {}: ".format(stock_B.ticker), np.mean(stock_B.closing_price)) 
print("s.d of {}: ".format(stock_B.ticker), np.std(stock_B.closing_price)) 
print("variance of {}: ".format(stock_B.ticker), np.var(stock_B.closing_price))