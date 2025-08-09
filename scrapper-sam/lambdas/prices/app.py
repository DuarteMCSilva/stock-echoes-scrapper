import yfinance
import pandas as pd


def handle_get_prices_request(event, context):
    try:
        request_ticker: str = event['queryStringParameters']['ticker']
        period: str = event['queryStringParameters']['p']
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': f'Missing parameter: {str(e)}',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Methods': 'POST, GET'
            }
        }

    historical_prices = process_historical_prices_by_date(request_ticker, period)

    close_prices = historical_prices[['Date', 'Close']] \
        .rename(columns={"Date": "date", "Close": "close"}) \
            .to_json(orient="records", compression="gzip")

    return {
        "statusCode": 200,
        "body": close_prices,
        "headers": {
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': 'http://localhost:4200',
            'Access-Control-Allow-Methods': 'POST, GET'
        }
    }

def process_historical_prices_by_date(ticker, period):
    history_df = fetch_historical_prices_from_api(ticker, period)

    if history_df.index.name == 'Date':
        history_df = history_df.reset_index()
    history_df['Date'] = pd.to_datetime(history_df['Date'])
    history_df['Date'] = history_df['Date'].dt.strftime('%Y%m%d')
    return history_df

def fetch_historical_prices_from_api(ticker: str = None, period_input: str = ''):
    if ticker is None:
        return 'No ticker provided!'

    period = choose_valid_period(period_input)
    interval = choose_interval(period)

    ticker = yfinance.Ticker(ticker)
    return ticker.history(period=period, interval=interval)

def choose_valid_period(period_input: str = ''):
    possible_vals = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    if period_input not in possible_vals:
        period = '5y'
    else:
        period = period_input

    return period

def choose_interval(period):
    if period == '5y':
        return '1wk'
    elif period == '10y':
        return '1mo'
    elif period == 'max':
        return '1wk'
    elif period == '1d':
        return '15m'
    elif period == '5d':
        return '90m'
    else:
        return '1d'
