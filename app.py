import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import yfinance as yf
from datetime import datetime as dt

# Create a Dash instance
app = dash.Dash(__name__)
server = app.server

# Define the layout of the application
app.layout = html.Div([
    # First division for inputs
    html.Div([
        html.P("Welcome to the Stock Dash App!", className="start"),
        html.Div(className="right-section", children=[
            dcc.Input(id='stock-code-input', type='text', placeholder='Enter Stock Code', className='stock-input'),
            html.Button('Submit', id='submit-stock-code', n_clicks=0, className='submit-button'),
        ]),
        html.Div([
            html.Label('Start Date:', className='date-picker-label'),
            dcc.DatePickerSingle(
                id='start-date-picker',
                date=dt.today(),
                display_format='YYYY-MM-DD',
                placeholder='Select Start Date',
                className='date-picker'
            )
        ], className='input-group'),
        html.Div([
            html.Button('Stock Price', id='stock-price-btn', className='button'),
            html.Button('Indicators', id='indicators-btn', className='button'),
            dcc.Input(id='forecast-days-input', type='number', placeholder='Days to Forecast', className='forecast-input'),
            html.Button('Forecast', id='forecast-btn', className='button'),
        ], className='input-group'),
    ], className="nav"),
    
    # Second division for data plots and company's basic information
    html.Div(className="left-section", children=[
        html.Div(id="company-info", className="header"),
        html.Div(id="description", className="description_ticker"),
        html.Div(id="graphs-content", className="graphs-content"),
        html.Div(id="main-content", className="main-content"),
        html.Div(id="forecast-content", className="forecast-content")
    ])
])

# Callback for updating company information
@app.callback(
    Output("company-info", "children"),
    Input("submit-stock-code", "n_clicks"),
    State("stock-code-input", "value")
)
def update_company_info(n_clicks, stock_code):
    if n_clicks > 0 and stock_code:
        ticker = yf.Ticker(stock_code)
        info = ticker.info
        company_name = info.get('longName', 'N/A')
        logo_url = info.get('logo_url', '')
        description = info.get('longBusinessSummary', 'No description available.')
        return html.Div([
            html.Img(src=logo_url, height="100px"),
            html.H3(company_name),
            html.P(description)
        ])
    return "Enter a stock code and click submit."

# Callback for updating stock price graph
@app.callback(
    Output("graphs-content", "children"),
    Input("stock-price-btn", "n_clicks"),
    [State("stock-code-input", "value"),
     State("start-date-picker", "date")]
)
def update_stock_graph(n_clicks, stock_code, start_date):
    if n_clicks > 0 and stock_code and start_date:
        df = yf.download(stock_code, start=start_date)
        if not df.empty:
            fig = px.line(df.reset_index(), x='Date', y=['Open', 'Close'], title=f"{stock_code} Opening and Closing Prices")
            return dcc.Graph(figure=fig)
        else:
            return "No data available for the given stock code and date."
    return "Enter a stock code, select a start date, and click 'Stock Price'."

# Callback for updating EMA graph
@app.callback(
    Output("main-content", "children"),
    Input("indicators-btn", "n_clicks"),
    [State("stock-code-input", "value"),
     State("start-date-picker", "date")]
)
def update_indicator_graph(n_clicks, stock_code, start_date):
    if n_clicks > 0 and stock_code and start_date:
        df = yf.download(stock_code, start=start_date)
        if not df.empty:
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            fig = px.line(df.reset_index(), x='Date', y='EMA_20', title=f"{stock_code} 20-Day EMA")
            return dcc.Graph(figure=fig)
        else:
            return "No data available for the given stock code and date."
    return "Enter a stock code, select a start date, and click 'Indicators'."

if __name__ == '__main__':
    app.run_server(debug=True)
