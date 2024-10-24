from .stock import Stock


class Portfolio:
    def __init__(self, email, db):
        self.email = email
        self.db = db
        self.portfolio = self.db.Portfolio.find_one({"email": self.email})
        if not self.portfolio:
            raise Exception("Portfolio not found")

    def get_current_balance(self):
        return self.portfolio['balance']

    def update_balance(self, new_balance):
        self.db.Portfolio.update_one({"email": self.email}, {"$set": {"balance": new_balance}})

    def get_stock(self, symbol):
        # Ensure portfolio is a dictionary, defaulting to an empty dict if it's not
        stocks = self.portfolio.get('portfolio', {})
        # If stocks is not a dictionary (e.g., if it's a string), convert it to an empty dict
        if not isinstance(stocks, dict):
            stocks = {}

        return stocks.get(symbol)

    def add_stock(self, symbol, shares, buy_price):
        stock = self.get_stock(symbol)
        stocks = self.portfolio.get('portfolio', {})
        if stock:
            # Update existing stock with the new purchase
            total_shares = stock['shares'] + shares
            avg_price = ((stock['shares'] * stock['buy_price']) + (shares * buy_price)) / total_shares
            stocks[symbol] = {'shares': total_shares, 'buy_price': avg_price}
        else:
            # Add new stock to the portfolio
            stocks[symbol] = {'shares': shares, 'buy_price': buy_price}

        # Update the portfolio in the database
        self.db.Portfolio.update_one({"email": self.email}, {"$set": {"portfolio": stocks}})

    def sell_stock(self, symbol, shares_to_sell):
        # Check if the user has the stock in their portfolio
        stocks = self.portfolio.get('portfolio', {})

        if symbol not in stocks:
            return {"message": "Stock not found in portfolio", "status": 404}

        stock_data = stocks[symbol]
        current_shares = stock_data['shares']

        # Check if the user has enough shares to sell
        if current_shares < shares_to_sell:
            return {"message": "Insufficient shares to sell", "status": 406}

        # Update shares
        new_shares = current_shares - shares_to_sell
        net_of_buying_shares = shares_to_sell * stock_data['buy_price']

        # If no shares left, remove the stock from the portfolio
        if new_shares == 0:
            del stocks[symbol]
        else:
            stocks[symbol]['shares'] = new_shares

        # Update the portfolio in the database
        self.db.Portfolio.update_one(
            {"email": self.email},
            {"$set": {"portfolio": stocks}}
        )

        # Calculate the total selling price
        stock = Stock(symbol)
        sell_price = stock.get_current_price()
        total_sale = sell_price * shares_to_sell

        # Update user's balance (assuming a method to get the current balance exists)
        current_balance = self.get_current_balance()
        new_balance = current_balance + total_sale
        self.update_balance(new_balance)

        return {
            "message": "Stock sold successfully",
            "symbol": symbol,
            "shares_sold": shares_to_sell,
            "total_sale": total_sale,
            "net_of_buying_shares":net_of_buying_shares,
            "new_balance": new_balance,
            "remaining_shares": new_shares,
            "status": 200
        }



