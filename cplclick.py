import csv
import os

import typer
import requests

app = typer.Typer()

COIN_GECKO_SIMPLE_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}"

def _read_portfolio_dict():
    if os.path.exists("portfolio.csv"):
        with open("portfolio.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            data = dict(
                [(row[0], float(row[1])) for row in reader]
            )
        return data
    return {}

def _write_portfolio_dict(data):
    with open("portfolio.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for (coin_id, quantity) in data.items():
            if float(quantity) > 0:
                writer.writerow([coin_id, quantity])

@app.command(short_help="search for a coin")
def search(
    coin,
    currency = typer.Option("usd")
    ):
    coin_data = requests.get(COIN_GECKO_SIMPLE_PRICE_URL.format(coin, currency)).json()
    print(f"The current price of {coin} is {coin_data[coin][currency]}")

@app.command(short_help="view your portfolio")
def portfolio(
    coin_id = typer.Option(None),
    currency = typer.Option("usd")
):
    data = _read_portfolio_dict()
    coin_data = requests.get(COIN_GECKO_SIMPLE_PRICE_URL.format(",".join(data.keys()), currency)).json()

    if coin_id is None:
        for (coin_id, quantity) in data.items():
            print(f"{quantity} {coin_id} with {quantity * coin_data[coin_id][currency]}")
    else:
        print(f"{data[coin_id]} {coin_id} worth {data[coin_id] * coin_data[coin_id][currency]}")

@app.command(short_help="buy coins")
def buy(
    coin_id = typer.Option(...),
    quantity: float = typer.Option(...)
):
    data = _read_portfolio_dict()

    if coin_id in data:
        data[coin_id] = float(data[coin_id]) + quantity
    else:
        data[coin_id] = quantity

    _write_portfolio_dict(data)

@app.command(short_help="sell coins")
def sell(
    coin_id = typer.Option(...),
    quantity: float = typer.Option(...)
):
    data = _read_portfolio_dict()

    if coin_id in data:
        data[coin_id] = float(data[coin_id]) - quantity

    _write_portfolio_dict(data)

if __name__ == "__main__":
    app()
