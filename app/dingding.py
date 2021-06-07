import requests,json

# windows
from app.authorization import dingding_token, dingding_secret, recv_window,api_secret,api_key
from app.BinanceAPI import BinanceAPI

import time
import hmac
import hashlib
import base64
import urllib.parse
# linux
# from app.authorization import dingding_token

class Message:

    def buy_market_msg(self, market, quantity):
        try:
            res = BinanceAPI(api_key,api_secret).buy_market(market, quantity)
            if res['orderId']:
                buy_info = "报警：币种为：{cointype}。买单量为：{num}".format(cointype=market,num=quantity)
                self.dingding_warn(buy_info)
                return res
        except BaseException as e:
            error_info = "报警：币种为：{cointype},买单失败.".format(cointype=market)
            self.dingding_warn(error_info)


    def sell_market_msg(self,market, quantity):
        '''
        :param market:
        :param quantity: 数量
        :param rate: 价格
        :return:
        '''
        try:
            res = BinanceAPI(api_key,api_secret).sell_market(market, quantity)
            if res['orderId']:
                buy_info = "报警：币种为：{cointype}。卖单量为：{num}".format(cointype=market,num=quantity)
                self.dingding_warn(buy_info)
                return res
        except BaseException as e:
            error_info = "报警：币种为：{cointype},卖单失败".format(cointype=market)
            self.dingding_warn(error_info+str(res))
            return res

    def dingding_warn(self,text):
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        timestamp = str(round(time.time() * 1000))
        sign = self._sign(timestamp)
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s" % (dingding_token, timestamp, sign)
        json_text = self._msg(text)
        content = requests.post(api_url, json.dumps(json_text), headers=headers).content
        print(content)

    def _sign(self, timestamp):
        secret = dingding_secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    def _msg(self,text):
        json_text = {
            "msgtype": "text",
            "at": {
                "atMobiles": [
                    "11111"
                ],
                "isAtAll": False
            },
            "text": {
                "content": text
            }
        }
        return json_text

if __name__ == "__main__":
    msg = Message()
    msg.dingding_warn('提个醒: 你好啊')