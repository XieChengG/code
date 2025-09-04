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
    request_time_list = []
    request_time_greater_one_second = []
    upstream_response_time_list = []
    upstream_response_time_greater_one_second = []

    for dict_member in dict_data:
        upstream_status_list.append(dict_member.get("upstream_status"))
        request_time_list.append(dict_member.get("request_time"))
        upstream_response_time_list.append(dict_member.get("upstream_response_time"))

    for number in upstream_status_list:
        if number != 200:
            upstream_status_not_200.append(number)

    for req_time in request_time_list:
        if req_time > 1:
            request_time_greater_one_second.append(req_time)

    for upstream_resp_time in upstream_response_time_list:
        if upstream_resp_time > 1:
            upstream_response_time_greater_one_second.append(upstream_resp_time)

    return (
        upstream_status_not_200,
        request_time_greater_one_second,
        upstream_response_time_greater_one_second,
    )


def print_analysis_result(*args, **kwargs):
    print_str = """------------ANALYSE RESULT------------
    反向代理响应码非200的个数: {0}
    请求耗时大于1秒的个数: {1}
    反向代理响应时间大于1秒的个数: {2}"""
    print(print_str.format(len(args[0]), len(args[1]), len(args[2])))


if __name__ == "__main__":
    try:
        file = "/".join([base_dir, "nginx.log"])
        data = transfer_dict(file)

        (
            upstream_status_not_200,
            request_time_greater_one_second,
            upstream_resp_time_greater_one_second,
        ) = analysis(data)

        print_analysis_result(
            upstream_status_not_200,
            request_time_greater_one_second,
            upstream_resp_time_greater_one_second,
        )
    except Exception as e:
        print(e)
