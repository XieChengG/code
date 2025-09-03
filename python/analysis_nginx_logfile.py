import json
import os
import sys


base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)


def transfer_dict(file_name):
    """把nginx日志文件反序列化成字典"""
    dict_list = []
    with open(file_name, "r") as f:
        for line in f:
            dict_list.append(json.loads(line))
    return dict_list


def analysis(dict_data):
    """分析nginx日志文件"""
    upstream_status_list = []
    upstream_status_not_200 = []
    for dict_member in dict_data:
        upstream_status_list.append(dict_member.get("upstream_status"))

    for number in upstream_status_list:
        if number != 200:
            upstream_status_not_200.append(number)

    if len(upstream_status_not_200) > len(dict_data) / 2:
        return 1
    else:
        return 0


if __name__ == "__main__":
    try:
        file = "/".join([base_dir, "nginx.log"])
        print(file)
        data = transfer_dict(file)
        print(analysis(data))
    except Exception as e:
        print(e)
