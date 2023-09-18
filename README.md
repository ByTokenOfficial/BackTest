# **基於 Python BackTrader 框架開發的回測系統**
# binance_data_receiver.py
- 用於獲取幣安交易所中的歷史OHLCV資料
- 適用任意時框（限幣安API所支援時框，需要客製化時匡請使用 BuildKlines.py 檔案）
- 適用任意時間範圍
- 採用多線程抓取，適用於多幣種
# Utils 資料夾
- **BuildKlines.py**
    - 建構 K 棒
    - 時框重新取樣
    - K 棒完整性
- **DataframeConvertor.py**
    - 幣安資料轉 CSV 檔
    - JSON 格式資料轉 CSV 檔
# Indicators 資料夾
- **VolumeIndicator.py 指標範例**
    - 聲明 lines
    - 最小計算週期
    - lines 計算公式
# Strategies 資料夾
- **Template.py 策略模板**
    - 聲明參數 params
    - 初始化方法中包含變量用於 記錄訂單資料、記錄交易bar、OHLCV價格
    - next 方法中為策略進出場邏輯
    - notify_order 方法用於訂單狀態判斷
    - notify_trade 方法用於打印訂單結算時的盈虧狀態
    - log 為自定義的打印函數
    - stop 方法為最佳化參數時打印相關參數
# BackTester.py 策略回測器
- 需從 Strategies 資料夾中 import 策略
- 打印策略參數、最終金額、夏普率、最大回撤、年化報酬率、交易筆數、盈利筆數、虧損筆數、勝率、輸率、獲利因子
- 畫出回測結果圖
# Optimizator.py 參數優化器
- 需從 Strategies 資料夾中 import 策略
- 打印策略參數、最終金額
- 將所有參數回測資料儲存至 CSV 檔