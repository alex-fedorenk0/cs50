import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd, get_chart_data

import re

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    alert = request.args.get('alert')

    query = 'SELECT symbol, SUM(shares) AS num_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING num_shares > 0'
    portfolio = db.execute(query, session['user_id'])

    for stock in portfolio:
        data = lookup(stock['symbol'])
        stock['name'] = data['name']
        stock['price'] = data['price']
        stock['total'] = stock['num_shares'] * stock['price']

    balance = db.execute('SELECT cash FROM users WHERE id = ?', session['user_id'])[0]['cash']
    total = sum((stock['total'] for stock in portfolio)) + balance

    return render_template('index.html', data=portfolio, alert=alert, balance=balance, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        shares = request.form.get('shares')
        lookup_data = lookup(symbol)

        # Validate shares input
        if not(shares.isdigit()):
            return apology('Shares quantity must be positive integer', 400)

        if lookup_data:
            # Check for balance
            user_id = session.get("user_id")
            balance = db.execute('SELECT cash FROM users WHERE id = ?', user_id)[0]['cash']
            required_cash = lookup_data['price'] * int(request.form.get('shares'))

            if required_cash > balance:
                return apology('Not enough cash to buy shares')

            # Make transaction & update balance
            transaction_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            db.execute(
                'INSERT INTO transactions (user_id, symbol, shares, price, datetime) VALUES (?, ?, ?, ?, ?)',
                user_id, symbol, shares, lookup_data['price'], transaction_time)
            db.execute('UPDATE users SET cash = ? WHERE id = ?', balance - required_cash, session.get("user_id"))

            flash('Shares bought successfully')
            return redirect(url_for('index'))

        # Lookup returns None
        else:
            return apology('Invalid symbol')

    # GET blank form
    return render_template('buy.html')


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    query = 'SELECT * FROM transactions WHERE user_id = ?'
    history = db.execute(query, session['user_id'])

    return render_template('history.html', data=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == 'POST':
        lookup_data = lookup(request.form.get('symbol'))
        if lookup_data:
            chart_data = get_chart_data(lookup_data['symbol'])

            return render_template('quote.html', data=lookup_data, chart_data=chart_data)
        else:
            return apology('Invalid symbol')

    # GET blank form
    return render_template('quote.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide username", 400)

        username = request.form.get('username')

        # Check for username restrictions
        if len(username) > 20 or len(username) < 4:
            return apology('Username must be between 4 and 20 characters')

        regex = r'[a-zA-Z0-9_-]{4,22}'
        if not re.match(regex, username):
            return apology('Only letters, digits, underscore and hyphen are allowed')

        # Check if username is already used
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology('Username already exists')

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Please provide password", 400)

        password = request.form.get("password")
        # Check for password length
        if len(password) < 6:
            return apology('Password too short (must be at least 6 characters)', 400)

        # TODO: check for pasword restrictions

        # Check for password matching
        if not password == request.form.get('confirmation'):
            return apology('Password and confirmation do not match!', 400)

        # All checks pass
        hash = generate_password_hash(password)
        db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', username, hash)

        flash('Successfully registered. Please login')
        return render_template("login.html")


def get_shares():
    """ Returns available shares for current user_id """
    query = 'SELECT symbol, SUM(shares) AS total FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total > 0'
    shares = db.execute(query, session['user_id'])

    return {share['symbol']: share['total'] for share in shares}


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    available_shares = get_shares()

    if request.method == 'POST':
        symbol = request.form.get('symbol')
        shares = int(request.form.get('shares'))

        user_id = session.get("user_id")
        balance = db.execute('SELECT cash FROM users WHERE id = ?', user_id)[0]['cash']

        print(get_shares())  # TODO Remove debug

        # Check for having enough of selected shares
        if available_shares[symbol] < shares:
            return apology('Not enough shares to sell!')

        # Make sell transaction & update balance
        price = lookup(symbol)['price']
        transaction_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        received_cash = price * shares
        db.execute(
            'INSERT INTO transactions (user_id, symbol, shares, price, datetime) VALUES (?, ?, ?, ?, ?)',
            user_id, symbol, -shares, price, transaction_time)

        db.execute('UPDATE users SET cash = ? WHERE id = ?', balance + received_cash, user_id)
        flash('Shares sold successfully')
        return redirect(url_for('index'))

    # GET blank sell form
    symbol_list = sorted([key for key in available_shares.keys()])
    return render_template("sell.html", symbol_list=symbol_list)
