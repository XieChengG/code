#!/usr/bin/env python3

import ssl
import datetime
import time
import socket
import json
import os

domain_list = [
    "aftersale-admin.xmindtech.com",
    "battleace.xmindtech.com",
    "course-admin.xmindtech.com",
    "course.xmindtech.com",
    "download.xmindtech.com",
    "edu-admin.xmindtech.com",
    "edu.xmindtech.com",
    "event.xmindtech.com",
    "gcxl.xmindtech.com",
    "iedevs.xmindtech.com",
    "wework.xmindtech.com",
    "xut.xmindtech.com",
    "course-api.xmindtech.com",
    "edu-api.xmindtech.com",
    "playmp-api.xmindtech.com",
    "aftersale.xmindtech.com",
    "wiki.xmindtech.com",
    "test.test.xmindtech.com",
    "m.xmindtech.com",
    "www.xmindtech.com",
    "agent.test.xmindtech.com",
    "voice-copy.test.xmindtech.com",
    "www.battleace.cn",
    "api.battleace.cn",
    "logto.ai.bigs.top",
    "chatgpt-next.ai.bigs.top",
    "wework.ai.bigs.top",
    "voice-api.ai.bigs.top",
    "static.xoriginai.com",
    "xoriginai.com",
    "www.xoriginai.com",
    "logto-admin.ai.bigs.top",
    "webrtc.xoriginai.com",
    "xdc.aipi.com",
    "xdc-ota.xorigin.ai",
    "xdc.xorigin.ai",
    "xdc.xoriginai.com",
    "xdc-ota.xoriginai.com",
    "static.aipi.com"
]


# 获取域名的证书信息
def get_domain_cert(domain):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(), server_hostname=domain)
    conn.connect((domain, 443))
    cert = conn.getpeercert()
    return cert


# 获取证书的有效剩余天数
def get_time_delta(notbefore, notafter):
    notbefore_timestamp = time.mktime(time.strptime(notbefore, "%b %d %H:%M:%S %Y GMT"))
    notafter_timestamp = time.mktime(time.strptime(notafter, "%b %d %H:%M:%S %Y GMT"))
    current_timestamp = time.mktime(time.localtime())
    time_delta = notafter_timestamp - current_timestamp
    day_delta = time_delta / 86400
    return int(day_delta)


renew_domain_dict = {}


# 获取证书有效期小于20天的域名
def get_renew_domain():
    for domain in domain_list:
        cert_info = get_domain_cert(domain)
        time_delta = get_time_delta(cert_info['notBefore'], cert_info['notAfter'])
        if time_delta < 20:
            renew_domain_dict[domain] = time_delta


# 发送飞书告警信息
def send_renew_message(message):
    os.popen(f"/usr/bin/env python3 feishu_alert.py '%s'" % message)


if __name__ == '__main__':
    try:
        get_renew_domain()
        message = "证书未续期成功的域名：{0}".format(json.dumps(renew_domain_dict))
        if not renew_domain_dict:
            pass
        else:
            send_renew_message(message)
    except Exception as e:
        print(e)
