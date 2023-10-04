import requests
import json
import pandas as pd
import datetime as dt
import concurrent.futures

def get_binance_bars(symbol, interval, startTime, endTime):
 
    url = "https://api.binance.com/api/v3/klines"
 
    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))
    limit = '1000'
 
    req_params = {
                "symbol" : symbol,
                'interval' : interval,
                'startTime' : startTime,
                'endTime' : endTime,
                'limit' : limit
                }
 
    df = pd.DataFrame(json.loads(requests.get(url, params = req_params).text))
 
    if (len(df.index) == 0):
        print(f'No data fetched for {symbol} {interval} from {startTime} to {endTime}')
        return None
    
    df = df.iloc[:, 0:6]
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
 
    df.open      = df.open.astype("float")
    df.high      = df.high.astype("float")
    df.low       = df.low.astype("float")
    df.close     = df.close.astype("float")
    df.volume    = df.volume.astype("float")

    df.index = pd.to_datetime(df['datetime'], unit='ms')
    df.drop(columns=['datetime'], inplace=True)
    df.index.rename('datetime', inplace=True)
    
    return df


def get_data_in_range(symbol, interval, startTime, endTime):
    all_data = pd.DataFrame()
    limit = 1000  # Binance API 的单次请求限制
    interval_minutes = int(interval[:-1])  # 获取 interval 的数字部分
    if interval[-1] == 'h':
        interval_minutes *= 60
    elif interval[-1] == 'd':
        interval_minutes *= 1440
        
    # 设置初始的 endTime
    end = startTime + dt.timedelta(minutes=interval_minutes*limit)
    
    while startTime < endTime:
        print(f'Fetching {symbol} {interval} data from {startTime} to {end}')
        data = get_binance_bars(symbol, interval, startTime, end)
        all_data = pd.concat([all_data, data])
        # 更新 startTime 和 endTime
        startTime = end
        end = min(end + dt.timedelta(minutes=interval_minutes*limit), endTime)
        
    return all_data

def fetch_and_save(saved_dir, symbol, interval, startTime, endTime):
    filename = f'/{symbol}_{interval}.csv'
    data = get_data_in_range(symbol, interval, startTime, endTime)
    print("Saving data to " + saved_dir + filename)
    data.to_csv(saved_dir + filename)

def fetch_multiple_symbols(saved_dir, symbols, interval, startTime, endTime):
    # 多線程處理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(
            fetch_and_save,
            [saved_dir]*len(symbols),
            symbols,
            [interval]*len(symbols),
            [startTime]*len(symbols),
            [endTime]*len(symbols)
            )


if __name__ == '__main__':
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'TRXUSDT',
               'DOTUSDT', 'MATICUSDT', 'LTCUSDT', 'SHIBUSDT', 'TONUSDT', 'WBTCUSDT', 'BCHUSDT', 'AVAXUSDT',
               'LEOUSDT', 'XLMUSDT', 'LINKUSDT', 'UNIUSDT']
    interval = '1m'
    startTime = dt.datetime(2020, 6, 24)
    endTime = dt.datetime(2023, 8, 31)
    # 輸入儲存目錄的絕對路徑
    saved_dir = f'YOUR_DIR_PATH'
    fetch_multiple_symbols(saved_dir, symbols, interval, startTime, endTime)