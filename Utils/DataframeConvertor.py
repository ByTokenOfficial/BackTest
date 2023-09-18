import pandas as pd

def json_to_csv(json_list):
    for json_file in json_list:
        df = pd.read_json(json_file)
        csv_file = json_file[:-5] + '.csv'
        df.to_csv(csv_file, index=False)

def raw_to_csv(new_dir, filename):
    df = pd.read_csv(filename, index_col=0)
    df.index.rename('Time', inplace=True)
    df = df.drop(columns=['datetime', 'adj_close'])
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.to_csv(new_dir+file, index=True)


if __name__ == '__main__':
    # json_list = ['usdcusdt.json', 'tusdusdt.json']
    # json_to_csv(json_list=json_list)
    # print("轉換完成！")
    dir = 'YOUR_DIR_PATH'
    new_dir = 'YOUR_NEW_DIR_PATH'
    file_list = ['ADAUSDT_1m.csv', 'AVAXUSDT_1m.csv', 'BCHUSDT_1m.csv', 'BNBUSDT_1m.csv', 'BTCUSDT_1m.csv',
                 'DOGEUSDT_1m.csv', 'DOTUSDT_1m.csv', 'ETHUSDT_1m.csv', 'LINKUSDT_1m.csv', 'LTCUSDT_1m.csv',
                 'MATICUSDT_1m.csv', 'SHIBUSDT_1m.csv', 'SOLUSDT_1m.csv', 'TRXUSDT_1m.csv', 'UNIUSDT_1m.csv',
                 'WBTCUSDT_1m.csv', 'XLMUSDT_1m.csv', 'XRPUSDT_1m.csv']
    for file in file_list:
        raw_to_csv(new_dir=new_dir, filename=dir+file)