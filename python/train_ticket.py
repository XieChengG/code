import pickle
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import zipfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

# 代理信息
proxy_host = "proxy.quanminip.com"
proxy_port = 31100
proxy_user = "customer-202509168012081519"
proxy_pass = "UU2sGPVo"

# 创建插件文件
manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (
    proxy_host,
    proxy_port,
    proxy_user,
    proxy_pass,
)

# 将插件文件打包成.zip
plugin_file = "proxy_auth_plugin.zip"
with zipfile.ZipFile(plugin_file, "w") as zp:
    zp.writestr("manifest.json", manifest_json)
    zp.writestr("background.js", background_js)

options = Options()
options.add_extension(plugin_file)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


class BuyTicket(object):
    def __init__(self):
        self.from_station = input("请输入出发地：")
        self.to_station = input("请输入目的地：")
        self.depart_date = input("请输入出发日期（如2025-04-17）：")
        self.trains = input("请输入车次（如G1234,G1235）：").split(",")
        self.passengers = input("请输入乘客姓名（如张三,李四）：").split(",")
        self.id_card_number = input("请输入登录账号的身份证后4位：")

        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"  # 登录页面
        self.personal_url = "https://kyfw.12306.cn/otn/view/index.html"  # 个人中心
        self.left_ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"  # 余票查询
        self.passenger_url = (
            "https://kyfw.12306.cn/otn/confirmPassenger/initDc"  # 乘客信息
        )

        # 邮件配置
        self.from_email_addr = "xiechenggang1991@163.com"
        self.to_email_addr = "xiechenggang@yeah.net"  # 多个用逗号隔开
        self.smtp_server = "smtp.163.com"
        self.password = "xcg199109"
        self.subject = "12306购票成功"
        self.msg = MIMEText("恭喜，您在12306抢票成功，请及时支付！", "plain", "utf-8")
        self.msg["From"] = Header(self.from_email_addr, "utf-8")
        self.msg["To"] = Header(self.to_email_addr, "utf-8")
        self.msg["Subject"] = Header(self.subject, "utf-8")

        # 绕过 12306 反爬虫
        self.driver = webdriver.Chrome(options=options)  # 调用谷歌浏览器
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
            },
        )

    def login(self, username, password):
        """登录"""
        print("开始登录12306...")
        self.driver.get(self.login_url)

        WebDriverWait(self.driver, 100).until(EC.url_to_be(self.login_url))

        self.driver.find_element(By.ID, "J-userName").send_keys(
            username
        )  # 12306登录用户名
        self.driver.find_element(By.ID, "J-password").send_keys(
            password
        )  # 12306登录密码
        WebDriverWait(self.driver, 100).until(  # 检测登录按钮是否可点击
            EC.element_to_be_clickable((By.ID, "J-login"))
        )
        self.driver.find_element(By.ID, "J-login").click()

        self._input_id_card_number()

        # WebDriverWait(self.driver, 100).until(  # 判断是否登录成功
        #     EC.presence_of_element_located((By.CLASS_NAME, "login-user"))
        # )

        time.sleep(20)
        print("登录成功！")

        cookies = self.driver.get_cookies()
        print(f"cookies: {cookies}")
        filename = "cookies.txt"
        self.save_cookies(cookies, filename)
        print(f"Cookies 已保存到 {filename}")

        print(f"开始从 {filename} 加载Cookies...")
        self.load_cookies(filename)
        print(f"从 {filename} 加载Cookies完成...")
        # return cookies

    def save_cookies(self, cookies, filename):
        """保存Cookies到文件"""
        with open(filename, "wb") as f:
            pickle.dump(cookies, f)

    def load_cookies(self, filename):
        """从文件加载Cookies"""
        try:
            with open(filename, "rb") as f:
                cookies = pickle.load(f)

            self.driver.delete_all_cookies()
            for cookie in cookies:
                if "expiry" in cookie:
                    cookie["expiry"] = int(cookie["expiry"])
                self.driver.add_cookie(cookie)
            print(f"已从 {filename} 加载cookies")
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
        except Exception as e:
            print(f"加载Cookies时出错: {e}")

    def _input_id_card_number(self):
        """输入登录账号的身份证后4位"""
        try:
            WebDriverWait(
                self.driver, 100
            ).until(  # 检测是否有登录账号的身份证后4位输入框
                EC.visibility_of_element_located((By.ID, "id_card"))
            )
            self.driver.find_element(By.ID, "id_card").send_keys(
                self.id_card_number
            )  # 输入登录账号的身份证后4位

            WebDriverWait(self.driver, 100).until(  # 检测获取验证码按钮是否可点击
                EC.element_to_be_clickable((By.ID, "verification_code"))
            )
            self.driver.find_element(By.ID, "verification_code").click()
        except Exception as e:
            print(e)

    def auth_code(self):
        """验证码"""
        pass

    def query_ticket(self):
        """余票查询"""
        print("开始查询余票...")
        # WebDriverWait(self.driver, 100).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".btn"))
        # )
        # self.driver.find_element(By.CSS_SELECTOR, ".btn").click()  # 提示确认
        self.driver.get(self.left_ticket_url)  # 进入余票查询页面

        # WebDriverWait(self.driver, 100).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "#qd_closeDefaultWarningWindowDialog_id"))
        #
        # )
        # self.driver.find_element(By.CSS_SELECTOR, "#qd_closeDefaultWarningWindowDialog_id").click()
        print("输入出发地...")
        self.driver.find_element(By.ID, "fromStationText").click()  # 输入出发地
        self.driver.find_element(By.ID, "fromStationText").send_keys(self.from_station)
        self.driver.find_element(By.ID, "fromStationText").send_keys(Keys.ENTER)

        print("输入目的地...")
        self.driver.find_element(By.ID, "toStationText").click()  # 输入目的地
        self.driver.find_element(By.ID, "toStationText").send_keys(self.to_station)
        self.driver.find_element(By.ID, "toStationText").send_keys(Keys.ENTER)

        print("输入出发日期...")
        self.driver.find_element(By.ID, "train_date").clear()  # 输入出发日期
        self.driver.find_element(By.ID, "train_date").send_keys(self.depart_date)

    def buy_ticket(self):
        """购买车票"""
        count = 0
        while True:
            print("开始购买车票...")
            # self.driver.get(self.left_ticket_url)  # 进入余票查询页面
            # WebDriverWait(self.driver, 100).until(  # 检测查询按钮是否可点击
            #     EC.element_to_be_clickable((By.ID, "query_ticket"))
            # )
            self.driver.find_element(By.ID, "query_ticket").click()  # 点击查询

            WebDriverWait(self.driver, 100).until(  # 检测车次列表是否加载完成
                EC.presence_of_element_located(
                    (By.XPATH, ".//tbody[@id='queryLeftTable']/tr")
                )
            )

            tr_list = self.driver.find_elements(
                By.XPATH, ".//tbody[@id='queryLeftTable']/tr[not(@datatran)]"
            )  # 过滤掉灰色车次
            for tr in tr_list:
                try:
                    train_number = tr.find_element(By.CLASS_NAME, "number").text  # 车次
                    for train in self.trains:
                        if train == train_number:  # 如果车次在输入的车次列表中
                            left_ticker_td = tr.find_element(By.XPATH, ".//td[5]").text
                            if (
                                left_ticker_td == "有" or left_ticker_td.isdigit()
                            ):  # 如果该车次有票
                                print(train_number + " " + left_ticker_td + "票")
                                tr.find_element(
                                    By.CLASS_NAME, "btn72"
                                ).click()  # 点击该车次的预定按钮

                                WebDriverWait(
                                    self.driver, 100
                                ).until(  # 等待确认页面加载完成
                                    EC.url_to_be(self.passenger_url)
                                )

                                WebDriverWait(
                                    self.driver, 100
                                ).until(  # 等待乘客列表加载完成
                                    EC.presence_of_element_located(
                                        (
                                            By.XPATH,
                                            ".//ul[@id='normal_passenger_id']/li",
                                        )
                                    )
                                )
                                self.select_passenger()
                                self.driver.find_element(
                                    By.ID, "submitOrder_id"
                                ).click()  # 点击提交订单
                                self.wait_for_confirm()
                                confirm_btn = self.driver.find_element(
                                    By.ID, "qr_submit_id"
                                )
                                self.driver.execute_script(
                                    "arguments[0].click();", confirm_btn
                                )  # 点击确认订单
                                time.sleep(3)

                                # 如果一次点击不成功，则持续点击
                                try:
                                    while confirm_btn:
                                        confirm_btn = self.driver.find_element(
                                            By.ID, "qr_submit_id"
                                        )
                                        self.driver.execute_script(
                                            "arguments[0].click();", confirm_btn
                                        )
                                        print("恭喜，抢票成功！")
                                        res = self.email_notice()
                                        if res:
                                            os._exit(0)
                                        else:
                                            os._exit(1)
                                except Exception as e:
                                    print(e)
                                    os._exit(1)
                            else:
                                count += 1
                                print(
                                    f"您所抢的{train_number}暂时无票，正在尝试重试第{count}次"
                                )
                                time.sleep(0.001)
                except:
                    break

    def select_passenger(self):
        """选择乘客"""
        print("开始选择乘客...")
        passenger_list = self.driver.find_elements(
            By.XPATH, ".//ul[@id='normal_passenger_id']/li/label"
        )  # 获取乘客列表
        for passenger in passenger_list:
            if passenger.text in self.passengers:  # 如果乘客在输入的乘客列表中
                passenger.click()  # 选择该乘客

    def wait_for_confirm(self):
        """等待确认"""
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dhtmlx_wins_body_outer"))
        )

        WebDriverWait(self.driver, 100).until(  # 检测确认窗口是否加载完成
            EC.presence_of_element_located((By.ID, "qr_submit_id"))
        )

        WebDriverWait(self.driver, 100).until(  # 检测确认按钮是否可点击
            EC.element_to_be_clickable((By.ID, "qr_submit_id"))
        )

    def email_notice(self):
        """发送邮件通知"""
        try:
            smtp_obj = smtplib.SMTP_SSL(self.smtp_server)
            smtp_obj.connect(self.smtp_server, 465)
            smtp_obj.login(self.from_email_addr, self.password)
            smtp_obj.sendmail(
                self.from_email_addr,
                self.to_email_addr.split(","),
                self.msg.as_string(),
            )
            print("邮件发送成功！")
            smtp_obj.quit()
            return True
        except smtplib.SMTPException:
            print("邮件发送失败！")


if __name__ == "__main__":
    try:
        # cookies = []
        # filename = "cookies.txt"

        buy_ticket = BuyTicket()  # 实例化

        # buy_ticket.load_cookies(filename)
        buy_ticket.login("948369040@qq.com", "xcg1991")
        # buy_ticket.save_cookies(cookies, filename)

        buy_ticket.query_ticket()
        buy_ticket.buy_ticket()

    except Exception as e:
        print(e)
