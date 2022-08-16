from fastapi import FastAPI, status
import requests
from pydantic import BaseModel
from mongita import MongitaClientDisk


COIN_URL = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}"


class Investment(BaseModel):
    coin_id: str
    quantity: float


client = MongitaClientDisk()
db = client.portfolio
investments = db.investments 
app = FastAPI()


def get_single_price(coin_id="bitcoin", currency="usd", quantity=1.0):
    coin_url = COIN_URL.format(coin_id, currency)
    coin_data = requests.get(coin_url).json()
    coin_price = coin_data[coin_id][currency]
    return coin_price * quantity


def mongita_to_str(o):
    return dict([
        (key, o[key]) for key in o.keys() if key.lower() != "_id"
    ])


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/single_coin/{coin_id}")
@app.get("/single_coin/{coin_id}/{currency}")
@app.get("/single_coin/{coin_id}/{currency}/{quantity}")
def single_coin(coin_id: str, currency: str = "usd", quantity: float = 1.0):
    coin_price = get_single_price(coin_id, currency, quantity)
    return {coin_id: coin_price}


@app.get("/portfolio")
@app.get("/portfolio/{currency}")
def list_portfolio(currency="usd"):
    coin_ids = [coin["coin_id"] for coin in investments.find()]
    response = requests.get(COIN_URL.format(",".join(coin_ids), currency))
    coin_data = response.json()
    all_investments = dict(
        [(coin_id, coin_data[coin_id][currency] * investments.find_one({"coin_id": coin_id})["quantity"]) for coin_id in coin_ids]
    )
    total_value = sum([value for (_, value) in all_investments.items()])
    return {
        "investments": all_investments,
        "total_value": total_value
    }


@app.get("/portfolio/coin/{coin_id}")
@app.get("/portfolio/coin/{coin_id}/{currency}")
def list_portfolio_by_coin_id(coin_id, currency="usd"):
    response = requests.get(COIN_URL.format(coin_id, currency))
    coin_data = response.json()
    investment = investments.find_one({"coin_id": coin_id})
    return {
        "coin_id": coin_id,
        "total_value": coin_data[coin_id][currency] * investment["quantity"],
        "quantity": investment["quantity"]
    }


@app.post("/portfolio", status_code=status.HTTP_201_CREATED)
def new_investment(investment: Investment):
    investments.insert_one(investment.dict())
    return investment


@app.put("/portfolio", status_code=status.HTTP_204_NO_CONTENT)
def update_investment(investment: Investment):
    investments.update_one({"coin_id": investment.coin_id}, {"$inc": {"quantity": investment.quantity}})
    if investments.find_one({"coin_id": investment.coin_id})["quantity"] <= 0:
        investments.delete_one({"coin_id": investment.coin_id})


@app.delete("/portfolio/{coin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(coin_id):
    investments.delete_one({"coin_id": coin_id})
