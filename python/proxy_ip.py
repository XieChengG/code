import requests

target_url = "http://myip.ipip.net"

proxy_host = "proxy.quanminip.com"
proxy_port = 31100

proxy_meta = "http://customer-202509168012081519:UU2sGPVo@%(host)s:%(port)s" % {
    "host": proxy_host,
    "port": proxy_port,
}

proxies = {"http": proxy_meta, "https": proxy_meta}

response = requests.get(target_url, proxies=proxies, timeout=20)
print(response.text)
