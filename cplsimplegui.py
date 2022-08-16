import PySimpleGUI as sg
import requests

coins = [] # hack .. I think

coin_list = [
    [sg.Listbox(values=[], size=(40, 10), key="-PORTFOLIO-")],
    [sg.Button("Get Value", key='-GET_COIN_VALUE-')],
    [sg.Text("", key="-COIN_VALUE-")]
]

buy_sell = [
    [sg.Text("Coin ID"), sg.Input("", key="-COIN_ID_BUY_SELL-")],
    [sg.Text("Quantity"), sg.Input("", key="-QUANTITY-")],
    [sg.Button("Buy", key="-BUY-"), sg.Button("Sell", key="-SELL-")]
]

layout = [
    [sg.Input("", key="-COIN_ID_SEARCH-"), sg.Button("Search", key="-SEARCH-")],
    [sg.Text("", key="-TOTAL_VALUE-")],
    [sg.Column(coin_list), sg.Column(buy_sell)],
]

window = sg.Window("Crypto Tracker", layout, finalize=True)

def refresh_portfolio():
    portfolio = requests.get("http://127.0.01:8000/portfolio").json()
    global coins # more hack
    coins = sorted([key for key in portfolio["investments"].keys()])
    listbox = window["-PORTFOLIO-"]
    listbox.update(coins)
    text = window["-TOTAL_VALUE-"]
    text.update(f"Your Portfolio Value: {portfolio['total_value']}")
    window["-COIN_VALUE-"].update(f"")

refresh_portfolio()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "-SEARCH-":
        coin_id = values["-COIN_ID_SEARCH-"]
        coin_data = requests.get(f"http://127.0.0.1:8000/single_coin/{coin_id}").json()
        sg.popup(f"The current price of {coin_id} is {coin_data[coin_id]}")
    elif event == "-BUY-":
        coin_id = values["-COIN_ID_BUY_SELL-"]
        quantity = float(values["-QUANTITY-"])
        if coin_id in coins:
            r = requests.put("http://127.0.0.1:8000/portfolio", json={"coin_id": coin_id, "quantity": quantity})
        else:
            r = requests.post("http://127.0.0.1:8000/portfolio", json={"coin_id": coin_id, "quantity": quantity})
        refresh_portfolio()
    elif event == "-SELL-":
        coin_id = values["-PORTFOLIO-"]
        quantity = float(values["-QUANTITY-"])
        r = requests.put("http://127.0.0.1:8000/portfolio", json={"coin_id": coin_id[0], "quantity": (quantity * -1)})
        refresh_portfolio()
    elif event == "-GET_COIN_VALUE-":
        selected_coins = values["-PORTFOLIO-"]
        if len(selected_coins) == 1:
            coin_id = selected_coins[0]
            r = requests.get(f"http://127.0.0.1:8000/portfolio/coin/{coin_id}").json()
            window["-COIN_VALUE-"].update(f"You have {r['quantity']} {r['coin_id']} worth {r['total_value']} ")

window.close()
