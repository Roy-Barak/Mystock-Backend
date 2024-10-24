import yfinance as yf

apple_stock = yf.Ticker('AAPl')
# history = apple_stock.history(peroid='1d', interval='1m')
print (apple_stock.info)

