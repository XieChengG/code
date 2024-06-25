#!/usr/bin/env python3

import requests
import json
import sys
import hashlib
import hmac
import base64
import time


def send_msg(url, reminders, msg):
    timestamp = int(time.time())
    secret = ""
    sign = gen_sign(timestamp, secret)
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "at": {
            "atMobiles": reminders,
            "isAtAll": False
        },
        "content": {
            "text": msg
        }
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.text


def gen_sign(timestamp, secret):
    string_to_sign = '{}\n{}'.format(timestamp, secret)  # 拼接timestamp和secret
    hmac_code = hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')  # 对结果进行base64编码
    return sign


if __name__ == '__main__':
    try:
        msg = sys.argv[1]
        reminders = []
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/65df2c3a-fb3e-4eac-9c73-c5cf59e00101"
        print(send_msg(url, reminders, msg))
    except Exception as e:
        print("Usage: %s %s" % (sys.argv[0], "MSG"))
