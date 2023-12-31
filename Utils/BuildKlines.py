import pandas as pd
import mplfinance as mpf
import json

def convert_mpl_format(df, timestamp_col='Time', freq_range=None):
    # 轉換時間DateTime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # 指定openTime為index
    df.set_index(timestamp_col, inplace=True)

    if timestamp_col != 'Time':
        # 將索引名稱改為'datetime'
        df.index.rename('Time', inplace=True)

    # 更改columns的名稱，以讓mplfinance看得懂
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    # 插值法填充，使用二階多項式插值
    # df = df.interpolate(method='polynomial', order=2)

    if freq_range is None:
        return df
    else:
        return df.iloc[-1*freq_range:,:]
    
def save_mpl_format(df, filename, freq='H'):
    if freq != 'H':
        df = resample_dataframe(df=df, freq=freq)
    if filename.find('_'):
        i = filename.index('_')
        df.to_csv(f'{filename[:i]}_{freq}.csv', index=True)
    elif filename[-4:] == ".csv":
        df.to_csv(f'{filename[:-4]}_{freq}.csv', index=True)
    else:
        df.to_csv(f'{filename}_{freq}.csv', index=True)

def resample_dataframe(df, freq):
    new_df = df.resample(freq).agg({
                                    'Open': 'first',
                                    'High': 'max',
                                    'Low': 'min',
                                    'Close': 'last',
                                    'Volume': 'sum'
                                    })
    return new_df

def check_dataframe_integrity(df, time_start, time_end, freq):
    # 創建時間範圍
    date_range = pd.date_range(start=time_start, end=time_end, freq=freq)

    # 檢查索引是否完整
    missing_dates = date_range[~date_range.isin(df.index)]

    return missing_dates

def save_missing_dates_to_json(date_range, filename):
    # 將缺失的日期轉換為字符串，因為JSON不支持日期對象
    missing_dates_str = date_range.strftime('%Y-%m-%d %H:%M:%S').tolist()

    # 將缺失的日期保存到JSON文件
    with open(f'{filename}-MissingDates.json', 'w') as f:
        json.dump(missing_dates_str, f)

    print('Missing dates saved to JSON file.')

def calculate_missing_ratio(filename):
    df = pd.read_csv(filename)
    new_df = convert_mpl_format(df=df)
    time_start, time_end = df.index[0], df.index[-1] 
    missing_dates = check_dataframe_integrity(df=new_df, time_start=time_start, time_end=time_end, freq='H')
    save_missing_dates_to_json(date_range=missing_dates, filename=filename)
    date_range = pd.date_range(start=time_start, end=time_end, freq='H')
    missing_ratio = len(missing_dates) / len(date_range)
    print('Total Data Length:', len(date_range))
    print('Missing ratio:', missing_ratio)

def build_klines(filename, freq):
    df = pd.read_csv(filename)
    new_df = convert_mpl_format(df=df)
    resample_df = resample_dataframe(df=new_df, freq=freq)
    # mpf.plot(resample_df, type='candle', volume=True)
    return resample_df

def resample_klines_save(filename, freq):
    df = pd.read_csv(filename)
    new_df = convert_mpl_format(df=df)
    save_mpl_format(df=new_df, filename=filename, freq=freq)


if __name__ == '__main__':
    abs_path = "YOUR_DIR"
    filename = "BTCUSDT_1m.csv"
    timeframe_list = ['1H', '4H', '1D']
    for f in timeframe_list:
        print(f'Resampling {filename} to {f} timeframe ...')
        resample_klines_save(filename=abs_path+filename, freq=f)