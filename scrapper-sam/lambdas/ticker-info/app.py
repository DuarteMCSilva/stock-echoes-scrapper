import yfinance
import json
import numbers


def get_info(event, context):
    try:
        request_ticker: str = event['queryStringParameters']['ticker']
        if request_ticker is None or request_ticker.strip() == '':
            raise Exception("Ticker parameter is missing or empty.")
    except Exception as e:
        return {
            'statusCode': 400,
            'body': f'Missing parameter: {e}',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Methods': 'POST, GET'
            }
        }

    try:
        ticker = getTicker(request_ticker)
        info = getInfo(ticker)
        financials = {
            'ticker': request_ticker,
            'info': info,
        }

        return {
            'statusCode': 200,
            'body': json.dumps(financials),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Methods': 'POST, GET'
            }
        }
    except Exception as e:
        print(financials)
        return {
            'statusCode': 500,
            'body': f'Error fetching financial data: {str(e)}',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Methods': 'POST, GET'
            }
        }



def getTicker(ticker):
    try:
        ticker = yfinance.Ticker(ticker)
        return ticker
    except Exception as e:
        print(f'Error fetching ticker: {str(e)}')
        raise Exception(f'Error fetching ticker: {str(e)}')

def getInfo(ticker):
    try:
        info = ticker.info
        return info
    except Exception as e:
        raise Exception(f'Error fetching info: {str(e)}')

def safeReadNumber(df, column, index = None):
    value = safeReadFromDataFrame(df, column, index)

    if not isinstance(value, numbers.Number):
        print(f"Error reading from DataFrame: {column}, {index}")
        return 0

    return value

def safeReadFromDataFrame(df, column, index = None):
    try:
        if index != None:
            value = df[column]
        else: 
            value = df[column].iloc[index]
        return value
    except (AttributeError, KeyError, IndexError):
        print(f"Error reading from DataFrame: {column}, {index}")
        return "Unknown"
