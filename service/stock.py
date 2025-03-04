import yfinance as yf

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = yf.Ticker(self.symbol).info

    def get_stock_info(self):
        stock_info = {
            'name': self.data.get('longName', 'Unknown'),
            'previous_close': self.data.get('previousClose', None),
            'current_price': self.data.get('currentPrice', None),
            'market_open': self.data.get('regularMarketOpen', None),
            'market_close': self.data.get('regularMarketPreviousClose', None)
        }
        return [stock_info, self.data]

    def get_current_price(self):
        """
        Returns the current price of the stock.
        """
        return self.data.get('currentPrice', None)


# print(Stock('^OEX').get_stock_info())
#
# print(Stock('^NYA').get_stock_info())