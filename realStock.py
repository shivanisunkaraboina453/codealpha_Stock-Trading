import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- STOCK MARKET DATA ----------------
# price + available quantity added
stocks = {
    "AAPL": {"price": 300, "quantity": 1000},
    "TSLA": {"price": 400, "quantity": 800},
    "AMZN": {"price": 270, "quantity": 1200},
    "MSFT": {"price": 420, "quantity": 900},
    "GOOGL": {"price": 390, "quantity": 1100}
}

# ---------------- SESSION STATE INIT ----------------
if "balance" not in st.session_state:
    st.session_state.balance = 100000

if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = []


# ---------------- BUY FUNCTION ----------------
def buy_stock(symbol, qty):
    stock = stocks[symbol]
    price = stock["price"]

    if qty > stock["quantity"]:
        st.error("Not enough stock available in market!")
        return

    total_cost = price * qty

    if total_cost > st.session_state.balance:
        st.error("Insufficient balance!")
        return

    # update balance
    st.session_state.balance -= total_cost

    # update market stock quantity
    stocks[symbol]["quantity"] -= qty

    # update portfolio
    if symbol in st.session_state.portfolio:
        st.session_state.portfolio[symbol] += qty
    else:
        st.session_state.portfolio[symbol] = qty

    # transaction log
    st.session_state.transactions.append({
        "Type": "BUY",
        "Stock": symbol,
        "Quantity": qty,
        "Price": price,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    st.success(f"Bought {qty} shares of {symbol}")


# ---------------- SELL FUNCTION ----------------
def sell_stock(symbol, qty):
    if symbol not in st.session_state.portfolio:
        st.error("You don't own this stock!")
        return

    if st.session_state.portfolio[symbol] < qty:
        st.error("Not enough shares to sell!")
        return

    price = stocks[symbol]["price"]
    total_gain = price * qty

    # update balance
    st.session_state.balance += total_gain

    # update portfolio
    st.session_state.portfolio[symbol] -= qty
    if st.session_state.portfolio[symbol] == 0:
        del st.session_state.portfolio[symbol]

    # return stock to market (increase availability)
    stocks[symbol]["quantity"] += qty

    # transaction log
    st.session_state.transactions.append({
        "Type": "SELL",
        "Stock": symbol,
        "Quantity": qty,
        "Price": price,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    st.success(f"Sold {qty} shares of {symbol}")


# ---------------- UI ----------------
st.title("📈 Stock Trading Platform (Upgraded)")

# ---------------- MARKET DATA ----------------
st.subheader("📊 Market Data")

market_data = []
for s, data in stocks.items():
    market_data.append([s, data["price"], data["quantity"]])

st.table(pd.DataFrame(market_data, columns=["Stock", "Price", "Available Qty"]))


# ---------------- BUY SECTION ----------------
st.subheader("🟢 Buy Stocks")

buy_symbol = st.selectbox("Select Stock", list(stocks.keys()))
buy_qty = st.number_input("Quantity", min_value=1, step=1)

if st.button("Buy"):
    buy_stock(buy_symbol, buy_qty)


# ---------------- SELL SECTION ----------------
st.subheader("🔴 Sell Stocks")

sell_symbol = st.selectbox("Select Stock to Sell", list(stocks.keys()), key="sell")
sell_qty = st.number_input("Sell Quantity", min_value=1, step=1, key="sell_qty")

if st.button("Sell"):
    sell_stock(sell_symbol, sell_qty)


# ---------------- PORTFOLIO ----------------
st.subheader("💼 Portfolio")

st.write(f"💰 Balance: ₹{st.session_state.balance}")

total_value = st.session_state.balance

portfolio_list = []

for stock, qty in st.session_state.portfolio.items():
    price = stocks[stock]["price"]
    value = price * qty
    total_value += value

    portfolio_list.append([stock, qty, price, value])

if portfolio_list:
    st.table(pd.DataFrame(portfolio_list,
                          columns=["Stock", "Qty", "Price", "Value"]))
else:
    st.info("No stocks owned")

st.write(f"📊 Total Portfolio Value: ₹{total_value}")


# ---------------- TRANSACTIONS ----------------
st.subheader("📜 Transaction History")

if st.session_state.transactions:
    st.table(pd.DataFrame(st.session_state.transactions))
else:
    st.info("No transactions yet")
