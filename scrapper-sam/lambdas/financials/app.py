import yfinance
import json
import math


def handle_get_financials(event, context):
    try:
        request_ticker: str = event['queryStringParameters']['ticker']
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

    ticker = yfinance.Ticker(request_ticker)

    state = getStationaryFinancials(ticker)
    momentum = getFinancialsByDate(ticker)
    info = ticker.info
    currency = ticker.fast_info['currency']
    marketCap = ticker.fast_info['marketCap']
    shares = ticker.fast_info['shares']

    financials = {
        'ticker': request_ticker,
        'sector': info['sector'],
        'currency': currency,
        'marketCap': marketCap,
        'shares': shares,
        'beta': info['beta'],
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
            'revenue': getValuesWithRelativeChange(income_st.loc['Total Revenue'], data.get('revenue')),
            'grossProfit': getValuesWithRelativeChange(income_st.loc['Gross Profit'], data.get('grossProfit')),
            'netIncome': getValuesWithRelativeChange(income_st.loc['Net Income'], data.get('netIncome')),
            'fcf': getValuesWithRelativeChange(cash_flow_st.loc['Free Cash Flow'], data.get('fcf'))
        }

        momentum_metrics.append(data)
    
    return momentum_metrics

def getValuesWithRelativeChange(value, previous):

    if math.isnan(value):
            return { }

    if previous == None:
        return { 'value': value }

    previous_val = previous.get('value')

    if previous_val == None:
        return { 'value': value }

    change = value/previous_val

    if change < 0:
        return { 'value': value }

    return { 'value': value, 'change': change }

def getStationaryFinancials(ticker):
    last_balance_sheet = ticker.quarterly_balance_sheet

    current_metrics = {
        'debt': last_balance_sheet.loc['Total Debt'].iloc[0],
        'cash': last_balance_sheet.loc['Cash And Cash Equivalents'].iloc[0],
    }

    return current_metrics
