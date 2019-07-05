from datetime import datetime
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError


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

print("----{}----".format(ticker_a))
for i in range (0, len(a_data["timestamp"])):
    print(datetime.fromtimestamp(int(str(a_data["timestamp"][i])[:-3])), a_data["close"][i])

print("----{}----".format(ticker_b))
for i in range (0, len(b_data["timestamp"])):
    print(datetime.fromtimestamp(int(str(b_data["timestamp"][i])[:-3])), b_data["close"][i])