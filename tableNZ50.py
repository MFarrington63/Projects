#imports
import yfinance as yf
import pandas as pd
import requests
from io import StringIO
#Data Liberation
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://en.wikipedia.org/wiki/NZX_50_Index'

response = requests.get(url, headers=headers)
tables = pd.read_html(StringIO(response.text))
print(len(tables))
print(tables[0].head())
for i, table in enumerate(tables):
    print(f'Table {i}:')
    print(table.head(2))
    print()
nzx50 = tables[1]
print(nzx50.head(10))
print(nzx50.columns.tolist())
nzx50['Ticker'] = nzx50['Ticker symbol'] + '.NZ'
tickers = nzx50['Ticker'].tolist()
print(tickers)
#Getting rf -- It's all dynamic so I have hard coded it
RISK_FREE_RATE = 0.0379 #NZ 1y spot rate
#Data formatting
data = yf.download(tickers, start = '2021-01-01', end = '2026-06-24')['Close']
print(data.head())
print(data.shape)
#market cap finder
market_caps = {}
for ticker in tickers:
    try:
        info = yf.Ticker(ticker).info
        market_caps[ticker] = info.get('marketCap', None)
    except:
        market_caps[ticker] = None
print(market_caps)
#Changing data into something readable      
nzx50_indexed = nzx50.set_index('Ticker')[['Company', 'Sector']]
returns = data.pct_change().dropna(how='all')
print(returns.head())
print(returns.shape)
ann_returns = returns.mean() * 252
ann_vol = returns.std() * (252 ** 0.5)
sharpe = (ann_returns - RISK_FREE_RATE ) / ann_vol
output = pd.DataFrame({
    'ticker' : ann_returns.index,
    'company' : ann_returns.index.map(nzx50_indexed['Company']),
    'sector' : ann_returns.index.map(nzx50_indexed['Sector']),
    'market_cap' : ann_returns.index.map(market_caps),
    'ann_returns' : ann_returns.values,
    'ann_volatility' : ann_vol.values, 
    'sharpe_ratio' : sharpe.values
})
output = output.dropna()
output.to_csv('nzx50_metrics.csv', index=False)
print(f'Done. {len(output)} stocks saved to nzx50_metrics.csv')
print(output.head(10))
#END
#    'company' : nzx50.set_index('Ticker')['Company'],
#    'sector' : nzx50.set_index('Ticker')['Sector'],