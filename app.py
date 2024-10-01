from dash import Dash, html, dash_table, dcc, callback, Input, Output
import requests
import pandas as pd
import plotly.express as px
import datetime as dt
app = Dash()

#ticker drawdown callback in graph creation.

data = requests.get("http://127.0.0.1:8000/ticker/").json()
S = pd.Series(data[0]).to_frame()
S.index = pd.to_datetime(S.index)
S.reset_index(inplace=True)
S.columns = ["time", "price"]
S["dummy"] = [i for i in range(len(S))]

option_response = requests.get("http://localhost:8000/options/").json()
price, greek_info = option_response[0], option_response[1]
greeks = pd.DataFrame(greek_info)


fig = px.line(S, x="dummy", y="price")


app.layout = html.Div(children=[
    dcc.Input(
        id="ticker_input",
        placeholder="Ticker",
        type="text",
        value="SPY"
    ),
    dcc.Input(
        id="timestep_input",
        placeholder="valid intervals for yfinance api",
        type="text",
        value="1m"),
    dcc.Graph(
        id="ticker_price_series",
        figure=fig
    ),
    html.H1("options info. Won't work unless interval is 1d", style={"textAlign": "center"}),
    dcc.DatePickerSingle(
        id="option-expiry",
        min_date_allowed=dt.datetime.now().date() + dt.timedelta(days=1),
        date=dt.datetime.now().date()
    ),
    dcc.Input(
        id="strike_input",
        placeholder="strike price",
        type="text",
        value="500"),
    html.H3(
        id="option_price",
        children=f"{price}"
    ),
    dash_table.DataTable(greeks.to_dict(orient="records"), [{"name": i, "id": i} for i in greeks.columns])
]
    )

@callback(
    Output("ticker_price_series", "figure"),
    Input("ticker_input", "value"),
    Input("timestep_input", "value"))
def update_fig(ticker, interval):
    response = requests.get(f"http://localhost:8000/ticker/?ticker={ticker}&interval={interval}").json()
    series = pd.Series(response[0]).to_frame()
    series.columns = ["price"]
    series["n_steps"] = [i for i in range(len(series))]
    fig = px.line(series, x="n_steps", y="price", title=f"{ticker} {interval} data")
    fig.update_layout(transition_duration=100)
    return fig


if __name__ == '__main__':
    app.run(debug=True)