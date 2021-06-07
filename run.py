# -*- coding: utf-8 -*-
from app.BinanceAPI import BinanceAPI
from app.authorization import api_key,api_secret
from data.runBetData import RunBetData
from app.dingding import Message
from data.calcIndex import CalcIndex
import time

import mplfinance as mpf
import matplotlib as mpl# 用于设置曲线参数
from cycler import cycler# 用于定制线条颜色
import pandas as pd# 导入DataFrame数据
import matplotlib.pyplot as plt

binan = BinanceAPI(api_key,api_secret)
runbet = RunBetData()
msg = Message()

index = CalcIndex()

class Run_Main():

    def __init__(self):
        self.coinType = runbet.get_cointype()  # 交易币种
        pass


    def loop_run(self):
        while True:
            cur_market_price = binan.get_ticker_price(runbet.get_cointype()) # 当前交易对市价
            grid_buy_price = runbet.get_buy_price()  # 当前网格买入价格
            grid_sell_price = runbet.get_sell_price() # 当前网格卖出价格
            quantity = runbet.get_quantity()   # 买入量
            step = runbet.get_step() # 当前步数
            right_size = len(str(cur_market_price).split(".")[1])

            if grid_buy_price >= cur_market_price and index.calcAngle(self.coinType,"5m",False,right_size):   # 是否满足买入价
                res = msg.buy_market_msg(self.coinType, quantity)
                if res['orderId']: # 挂单成功
                    runbet.modify_price(cur_market_price, step+1) #修改data.json中价格、当前步数
                    time.sleep(60*2) # 挂单后，停止运行1分钟
                else:
                    break

            elif grid_sell_price < cur_market_price and index.calcAngle(self.coinType,"5m",True,right_size):  # 是否满足卖出价
                if step==0: # setp=0 防止踏空，跟随价格上涨
                    runbet.modify_price(grid_sell_price,step)
                else:
                    res = msg.sell_market_msg(self.coinType, runbet.get_quantity(False))
                    if res['orderId']:
                        # runbet.set_ratio(runbet.get_cointype()) 启动动态改变比率
                        runbet.modify_price(cur_market_price, step - 1)
                        time.sleep(60*2)  # 挂单后，停止运行1分钟
                    else:
                        break
            else:
                print("当前市价：{market_price}。未能满足交易,继续运行".format(market_price = cur_market_price))

    def macdCalc(self):
        kline = binan.get_klines("DOGEUSDT", "1m", 500)
        columns = ['开盘时间', 'Open', 'High', 'Low', 'Close', 'volume', '收盘时间',
                   '成交额', '成交笔数', '主动买入成交量', '主动买入成交额', '请忽略该参数']
        # df = pd.read_json('data/kline.json')
        df = pd.read_json(kline)
        df.columns = columns
        df['开盘时间'] = pd.to_datetime(df['开盘时间'], unit='ms')
        df = df.set_index('开盘时间').iloc[-10:, :5]

        # mpf.plot(df, type='candle',mav=(5,10,20))

        # MACD默认参数为12、26、9，计算过程分为三步，
        # 第一步计算EMA：
        # 12日EMA
        # EMA(12) = 2 / (12 + 1) * 今日收盘价(12) + 11 / (12 + 1) * 昨日EMA(12)
        df['ema12'] = 0
        df['ema12'] = (2 / (12 + 1) * df['Close']) + (11 / (12 + 1) * df['ema12'].shift(1))
        a = 2 / (12 + 1) * df['Close']
        b = 11 / (12 + 1) * df['ema12'].shift(1)
        df['ema123'] = a + b
        # 26日EMA
        # EMA(26) = 2 / (26 + 1) * 今日收盘价(26) + 25 / (26 + 1) * 昨日EMA(26)
        # 第二步计算DIFF：
        # DIFF = EMA(12) - EMA(26)
        # 第三步计算DEA：
        # DEA = 2 / (9 + 1) * 今日DIFF + 8 / (9 + 1) * 昨日DEA
        # 第四步计算MACD柱线：
        # MACD柱线 = 2 * (DIFF - DEA)
        print(df)

# if __name__ == "__main__":
#     instance = Run_Main()
#     try:
#         instance.loop_run()
#     except Exception as e:
#         error_info = "报警：币种{coin},服务停止.错误原因{info}".format(coin=instance.coinType,info=str(e))
#         msg.dingding_warn(error_info)

# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":
    instance = Run_Main()
    instance.macdCalc()
    # instance.loop_run()
