import pandas as pd

def json_to_csv(json_list):
    for json_file in json_list:
        df = pd.read_json(json_file)
        csv_file = json_file[:-5] + '.csv'
        df.to_csv(csv_file, index=False)

if __name__ == '__main__':
    json_list = ['usdcusdt.json', 'tusdusdt.json']
    json_to_csv(json_list=json_list)
    print("轉換完成！")