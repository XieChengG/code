import xlrd
import pandas as pd


def read_excel():
    wb = xlrd.open_workbook("book.xlsx")  # 打开excel表格
    sh = wb.sheet_by_name("book")  # 定位 excel 表格的数据页 sheet
    row_num = sh.nrows  # 有效数据行数
    col_num = sh.ncols  # 有效数据列数

    value1 = sh.cell(2, 0).value  # 输出第3行，第1列的值
    value2 = sh.row_values(0)  # 输出第一行所有的值
    value3 = sh.col_values(0)  # 输出第一列所有的值

    for i in range(row_num):  # 遍历除表头的所有数据
        if i == 0:
            continue
        print(sh.row_values(i))


read_excel()
