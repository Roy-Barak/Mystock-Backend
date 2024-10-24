from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from service.portfilo import Portfolio
from service.stock import Stock
from flask_pymongo import PyMongo
import bcrypt  # Import bcrypt for password hashing
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file
app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

# Initialize PyMongo
mongo = PyMongo(app)
jwt = JWTManager(app)


@app.route('/')
def index():
    return 'It works!'


# Stock route to get stock information
@app.route('/get/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    stock = Stock(symbol)
    stock_info = stock.get_stock_info()
    return jsonify(stock_info)


@app.route('/user-register', methods=['POST'])
def add_data():
    data = request.json

    # Check if the email is already in the db
    if mongo.db.Users.find_one({"email": data['email']}):
        return jsonify(message="Email already registered"), 402

    # Hash the password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Store the new user with the hashed password
    user_data = {
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password  # Store hashed password
    }
    portfolio_data = {
        "email": data['email'],
        "balance": 10000,
        "portfolio": {}
    }
    result = mongo.db.Users.insert_one(user_data)
    mongo.db.Portfolio.insert_one(portfolio_data)
    token = create_access_token(identity=data['email'])

    # Return a success message
    return jsonify(name=user_data['name'], token=token),200


@app.route('/user-login', methods=['POST'])
def login_data():
    data = request.json
    user = mongo.db.Users.find_one({"email": data['email']})

    # Check for user existence and password
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        # Create a JWT token using the user's email as the identity
        access_token = create_access_token(identity=user['email'])
        return jsonify(name=user['name'], token=access_token), 200
    else:
        return jsonify(message="Incorrect email or password"), 401


@app.route('/user/buy-stock', methods=['POST'])
@jwt_required()  # Protect this route with JWT
def buy_stock():
    data = request.json
    symbol = data['symbol']
    shares = int(data['shares'])
    email = get_jwt_identity()
    # Fetch stock data from yfinance
    stock = Stock(symbol)
    current_price = stock.get_current_price()

    # Check if stock price and number of shares are valid
    if not current_price or shares <= 0:
        return jsonify(message="Invalid stock data or number of shares"), 405

    # Fetch user portfolio
    try:
        portfolio = Portfolio(email, mongo.db)  # Pass mongo.db to the Portfolio class
    except Exception as e:
        return jsonify(message=str(e)), 404

    # Calculate the total cost of the stock purchase
    total_cost = current_price * shares

    # Check if the user has enough balance
    if portfolio.get_current_balance() < total_cost:
        return jsonify(message="Insufficient balance"), 406

    # Deduct the total cost from the user's balance
    new_balance = portfolio.get_current_balance() - total_cost
    portfolio.update_balance(new_balance)

    # Add the purchased stock to the user's portfolio
    portfolio.add_stock(symbol, shares, current_price)

    return jsonify(message="Stock purchased successfully", new_balance=new_balance,current_price=current_price), 200


@app.route('/user/data', methods=['GET'])
@jwt_required()  # Require a valid JWT token to access this route
def get_portfolio():
    email = get_jwt_identity()

    # Find the user's portfolio by email
    portfolio = mongo.db.Portfolio.find_one({"email": email})

    if portfolio:
        # Extract balance and stocks (ensure portfolio is a dict)
        balance = portfolio.get('balance', 0)
        stocks = portfolio.get('portfolio', {})

        # Return the portfolio and balance as a JSON response
        # Prepare a response to include stock prices
        stock_info = {}
        for symbol, stock_data in stocks.items():
            stock = Stock(symbol)
            stock_price = stock.get_stock_info()[0]
            current_price = stock_price['current_price']
            stock_info[symbol] = {
                "shares": stock_data['shares'],
                "buy_price": round(stock_data['buy_price'], 2),
                "current_price": round(current_price, 2),
                "previous_price": round(stock_price['previous_close'], 2),
                "profit_number": round(stock_data['shares']*(current_price-stock_data['buy_price']), 2),
                "profit_percentage": round(100 * (current_price-stock_data['buy_price'])/stock_data['buy_price'], 2)
            }

        # Return the portfolio and balance as a JSON response
        return jsonify({
            "email": email,
            "balance": balance,
            "stocks": stock_info
        }), 200
    else:
        return jsonify(message="Portfolio not found"), 404


@app.route('/user/sell-stock', methods=['POST'])
@jwt_required()  # Protect this route with JWT
def sell_stock():
    data = request.json
    symbol = data['symbol']
    shares = int(data['shares'])
    email = get_jwt_identity()
    # Fetch stock data from yfinance
    stock = Stock(symbol)
    current_price = stock.get_current_price()

    # Check if stock price and number of shares are valid
    if not current_price or shares <= 0:
        return jsonify(message="Invalid stock data or number of shares"), 405
    portfolio = Portfolio(email, mongo.db)
    response = portfolio.sell_stock(symbol, shares)
    if response['status'] == 200:
        return jsonify(response), response['status']
    else:
        return jsonify(message="Invalid stock data or number of shares"), response['status']


if __name__ == '__main__':
    app.run(debug=True)
