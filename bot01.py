import pydash as py_
import time

import csv

from bittrex import Bittrex
from messenger import Messenger

from logger import logger

import krakenex
import decimal
import time

pair = 'XXRPZEUR'
# NOTE: for the (default) 1-minute granularity, the API seems to provide
# data up to 12 hours old only!
since = str(1499000000) # UTC 2017-07-02 12:53:20
interval = str(1)

k = krakenex.API()
k.load_key('kraken.key')

def now():
    return decimal.Decimal(time.time())

def lineprint(msg, targetlen = 72):
    line = '-'*5 + ' '
    line += str(msg)

    l = len(line)
    if l < targetlen:
        trail = ' ' + '-'*(targetlen-l-1)
        line += trail

    print(line)
    return

while True:
    lineprint(now())

    before = now()
    ret = k.query_public('OHLC', data = {'pair': pair, 'interval': interval,'since': since})
    after = now()

    # comment out to track the same "since"
    # since = ret['result']['last']

    # TODO: don't repeat-print if list too short
    bars = ret['result'][pair]
 
    for b in bars[:5]: print(b)
    print('...')
    for b in bars[-5:]: print(b)

    lineprint(after - before)

    close_price = []
    close_price = bars[-1][4]
    print (close_price)

    

    time.sleep(60)

def get_closing_prices(self, coin_pair, period, unit):
        """
        Returns closing prices within a specified time frame for a coin pair
        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param period: Number of periods to query
        :type period: int
        :param unit: Ticker interval (one of: 'oneMin', 'fiveMin', 'thirtyMin', 'hour', 'week', 'day', and 'month')
        :type unit: str
        :return: Array of closing prices
        :rtype : list
        """
        historical_data = self.Bittrex.get_historical_data(coin_pair, period, unit)
        closing_prices = []
        for i in historical_data:
            closing_prices.append(i["C"])
        return closing_prices

def calculate_RSI(self, coin_pair, period, unit):
        """
        Calculates the Relative Strength Index for a coin_pair
        If the returned value is above 75, it's overbought (SELL IT!)
        If the returned value is below 25, it's oversold (BUY IT!)
        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param period: Number of periods to query
        :type period: int
        :param unit: Ticker interval (one of: 'oneMin', 'fiveMin', 'thirtyMin', 'hour', 'week', 'day', and 'month')
        :type unit: str
        :return: RSI
        :rtype : float
        """
        closing_prices = self.get_closing_prices(coin_pair, period * 3, unit)
        count = 0
        change = []
        # Calculating price changes
        for i in closing_prices:
            if count != 0:
                change.append(i - closing_prices[count - 1])
            count += 1
            if count == 15:
                break
        # Calculating gains and losses
        advances = []
        declines = []
        for i in change:
            if i > 0:
                advances.append(i)
            if i < 0:
                declines.append(abs(i))
        average_gain = (sum(advances) / 14)
        average_loss = (sum(declines) / 14)
        new_avg_gain = average_gain
        new_avg_loss = average_loss
        for _ in closing_prices:
            if 14 < count < len(closing_prices):
                close = closing_prices[count]
                new_change = close - closing_prices[count - 1]
                add_loss = 0
                add_gain = 0
                if new_change > 0:
                    add_gain = new_change
                if new_change < 0:
                    add_loss = abs(new_change)
                new_avg_gain = (new_avg_gain * 13 + add_gain) / 14
                new_avg_loss = (new_avg_loss * 13 + add_loss) / 14
                count += 1

        if new_avg_loss == 0:
            return None

        rs = new_avg_gain / new_avg_loss
        new_rs = 100 - 100 / (1 + rs)
        return new_rs
