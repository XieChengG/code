from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


class BuyTicket(object):
    def __init__(self):
        self.from_station = input("请输入出发地：")
        self.to_station = input("请输入目的地：")
        self.depart_date = input("请输入出发日期（如2025-04-17）：")
        self.trains = input("请输入车次（如G1234,G1235）：").split(",")
        self.passengers = input("请输入乘客姓名（如张三,李四）：").split(",")

        self.driver = webdriver.Chrome()  # 调用谷歌浏览器
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"  # 登录页面
        self.personal_url = "https://kyfw.12306.cn/otn/view/index.html"  # 个人中心
        self.left_ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"  # 余票查询
        self.passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"  # 乘客信息

    def login(self):
        """登录"""
        self.driver.get(self.login_url)
        script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'  # 绕过反爬虫
        self.driver.execute_script(script)

        WebDriverWait(self.driver, 100).until(
            EC.url_to_be(self.login_url)
        )

        self.driver.find_element(By.ID, "J-userName").send_keys("")  # 12306登录用户名
        self.driver.find_element(By.ID, "J-password").send_keys("")  # 12306登录密码
        WebDriverWait(self.driver, 100).until(  # 检测登录按钮是否可点击
            EC.element_to_be_clickable((By.ID, "J-login"))
        )
        self.driver.find_element(By.ID, "J-login").click()

    def auth_code(self):
        """验证码"""
        pass

    def query_ticket(self):
        """余票查询"""
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".btn"))
        )
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()  # 提示确认

        self.driver.get(self.left_ticket_url)  # 进入余票查询页面

        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#qd_closeDefaultWarningWindowDialog_id"))

        )
        self.driver.find_element(By.CSS_SELECTOR, "#qd_closeDefaultWarningWindowDialog_id").click()

        self.driver.find_element(By.ID, "fromStationText").click()  # 输入出发地
        self.driver.find_element(By.ID, "fromStationText").send_keys(self.from_station)
        self.driver.find_element(By.ID, "fromStationText").send_keys(Keys.ENTER)

        self.driver.find_element(By.ID, "toStationText").click()  # 输入目的地
        self.driver.find_element(By.ID, "toStationText").send_keys(self.to_station)
        self.driver.find_element(By.ID, "toStationText").send_keys(Keys.ENTER)

        self.driver.find_element(By.ID, "train_date").clear()  # 输入出发日期
        self.driver.find_element(By.ID, "train_date").send_keys(self.depart_date)

        WebDriverWait(self.driver, 100).until(  # 检测查询按钮是否可点击
            EC.element_to_be_clickable((By.ID, "query_ticket"))
        )

    def buy_ticket(self):
        """购买车票"""
        self.driver.find_element(By.ID, "query_ticket").click()  # 点击查询

        WebDriverWait(self.driver, 100).until(  # 检测车次列表是否加载完成
            EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
        )

        tr_list = self.driver.find_element(By.XPATH, ".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")  # 过滤掉灰色车次
        for tr in tr_list:
            train_number = tr.find_element(By.CLASS_NAME, "number").text  # 车次
            if train_number in self.trains:  # 如果车次在输入的车次列表中
                left_ticker_td = tr.find_element(By.XPATH, ".//td[4]").text
                if left_ticker_td == "有" or left_ticker_td.isdigit():  # 如果该车次有票
                    print(train_number + "有票")
                    self.driver.find_element((By.CLASS_NAME, "btn72")).click()  # 点击该车次的预定按钮

                    WebDriverWait(self.driver, 100).until(  # 等待确认页面加载完成
                        EC.url_to_be(self.passenger_url)
                    )

                    WebDriverWait(self.driver, 100).until(  # 等待乘客列表加载完成
                        EC.presence_of_element_located((By.XPATH, ".//ul[@id='normal_passenger_id']/li"))
                    )
                    self.select_passenger()
                    self.driver.find_element(By.ID, "submitOrder_id").click()  # 点击提交订单
                    self.wait_for_confirm()
                    confirm_btn = self.driver.find_element(By.ID, "qr_submit_id")
                    confirm_btn.click()

                    # 如果一次点击不成功，则持续点击
                    try:
                        while confirm_btn:
                            confirm_btn.click()
                            confirm_btn = self.driver.find_element(By.ID, "qr_submit_id")
                            print("恭喜，抢票成功！")
                            break
                    except Exception as e:
                        pass

    def select_passenger(self):
        """选择乘客"""
        passenger_list = self.driver.find_element(By.XPATH, ".//ul[@id='normal_passenger_id']/li/label")  # 获取乘客列表
        for passenger in passenger_list:
            if passenger.text in self.passengers:  # 如果乘客在输入的乘客列表中
                passenger.click()  # 选择该乘客

    def wait_for_confirm(self):
        """等待确认"""
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dhtmlx_wins_body_outer"))
        )

        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.ID, "qr_submit_id"))
        )

        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.ID, "qr_submit_id"))
        )
