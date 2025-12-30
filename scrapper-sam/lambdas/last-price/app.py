import yfinance as yf
import json

def get_last_price(event, context):
    params = event['queryStringParameters']

    ticker: str = params['ticker']
    if ticker.strip() == '':
        return buildHttpResponse(f'Missing parameter: Ticker parameter is missing or empty.', 400)

    try:
        price = fetch_last_price(ticker)
    except Exception as e:
        return buildHttpResponse(f'Failure while fetching financial data: {str(e)}', 500)

    result = {
        "symbol": ticker,
        "close": price,
        "change": None,
    }

    return buildHttpResponse(result, 200)

def fetch_last_price(ticker: str):
    yf_ticker = yf.Ticker(ticker)
    return yf_ticker.fast_info['lastPrice']

    
def buildHttpResponse(body, code):
    if code > 399:
        body = buildErrorObject(body)

    return {
        'statusCode': code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'http://localhost:4200',
            'Access-Control-Allow-Methods': 'POST, GET'
        }
    }

def buildErrorObject(message):
    return {
        'error': message
    }
