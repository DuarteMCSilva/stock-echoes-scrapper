import yfinance
import json
import math
import numbers


def handle_get_financials(event, context):
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
        state = getStationaryFinancials(ticker)
        momentum = getFinancialsByDate(ticker)
        fast_info = getFastInfo(ticker)
        currency = fast_info['currency']
        marketCap = fast_info['marketCap']
        shares = fast_info['shares']
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error fetching financial data: {str(e)}',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Methods': 'POST, GET'
            }
        }

    financials = {
        'ticker': request_ticker,
        'sector': safeReadFromDataFrame(info, 'sector'),
        'currency': currency,
        'marketCap': marketCap,
        'shares': shares,
        'beta': safeReadNumber(info, 'beta'),
        'state': state,
        'momentum': momentum
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
        print(info)
        return info
    except Exception as e:
        raise Exception(f'Error fetching info: {str(e)}')

def getFastInfo(ticker):
    fast_info = ticker.fast_info

    try:
        return {
        'currency': safeReadFromDataFrame(fast_info, 'currency'),
        'marketCap': safeReadNumber(fast_info, 'marketCap'),
        'shares': safeReadNumber(fast_info, 'shares')
    }
    except KeyError as e:
        print(f'Error fetching fast info: {str(e)}')
        return {
            'currency': 'Unknown',
            'marketCap': 0,
            'shares': 0
        }

def getFinancialsByDate(ticker):
    cash_flow = ticker.cash_flow
    income_statement = ticker.income_stmt

    dates = income_statement.columns.tolist()
    dates.reverse()

    momentum_metrics = []
    data = {}

    for date in dates:
        income_st = income_statement[date]
        cash_flow_st = cash_flow[date]
        format_date = date.strftime('%Y')


        data = {
            'period': format_date,
            'revenue': getValuesWithRelativeChange(safeReadNumber(income_st, 'Total Revenue'), data.get('revenue')),
            'grossProfit': getValuesWithRelativeChange(safeReadNumber(income_st, 'Gross Profit'), data.get('grossProfit')),
            'netIncome': getValuesWithRelativeChange(safeReadNumber(income_st, 'Net Income'), data.get('netIncome')),
            'fcf': getValuesWithRelativeChange(safeReadNumber(cash_flow_st, 'Free Cash Flow'), data.get('fcf'))
        }

        momentum_metrics.append(data)
    
    return momentum_metrics

def getValuesWithRelativeChange(value, previous):

    if math.isnan(value):
            return { }

    if previous == None:
        return { 'value': value }

    previous_val = previous.get('value')

    if (previous_val == None) or (previous_val == 0):
        return { 'value': value }

    change = value/previous_val

    if change < 0:
        return { 'value': value }

    return { 'value': value, 'change': change }

def getStationaryFinancials(ticker):
    last_balance_sheet = ticker.quarterly_balance_sheet

    debt = safeReadNumber(last_balance_sheet, 'Total Debt', 0)
    cash = safeReadNumber(last_balance_sheet, 'Cash And Cash Equivalents', 0)

    current_metrics = {
        'debt': debt,
        'cash': cash
    }

    return current_metrics

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
