#!/usr/bin/env python3

import random

def random_code():
    '''生成随机验证码'''
    while True:
        check_code = ""
        for i in range(5):
            current_code = random.randint(0, 4)
            if current_code == i:  # 大写字母
                check_code += str(chr(random.randint(65, 90)))
            else:  # 数字
                check_code += str(random.randint(0, 9))
        if not check_code.isalpha() and not check_code.isnumeric():  # 只打印出字母和数字的组合
            print("验证码：", check_code)
            exit(0)
        else:
            continue
random_code()