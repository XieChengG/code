#!/usr/bin/env python3


import hashlib
import os
import sys
import time

import tos


def calculate_md5(file_name):
    """计算文件的MD5哈希值"""
    md5 = hashlib.md5()

    try:
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):  # 分块读取文件，避免内存不足
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"计算MD5时出错：{str(e)}")
        return None


def init_tos_client(access_key, secret_key, endpoint, region):
    """初始化tos客户端"""
    try:
        client = tos.TosClientV2(
            ak=access_key,
            sk=secret_key,
            endpoint=endpoint,
            region=region,
        )
        return client
    except Exception as e:
        print(f"TOS客户端初始化失败:{str(e)}")
        return None


def get_file(base_dir, db_name, date_time):
    """获取本地上传文件的路径名"""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    file_name = db_name + "_" + date_time + ".gz"
    put_file_name = os.path.join(base_dir, file_name)

    if not os.path.isfile(put_file_name):
        print(f"文件{put_file_name}不存在")
        sys.exit(1)

    return put_file_name


def upload_file(bucket_name, put_file, client, object_key=None):
    """上传文件到火山引擎tos"""
    if not client:
        return {"success": False, "error": "TOS客户端未初始化"}

    # 判断本地文件是否存在
    if not os.path.isfile(put_file):
        return {"success": False, "error": "文件不存在"}

    # 计算文件MD5值
    local_md5 = calculate_md5(put_file)
    if not local_md5:
        return {"sucess": False, "error": "MD5计算失败"}

    # 设置对象建
    if not object_key:
        remote_path = "backup/database/postgresql"
        object_key = remote_path + "/" + os.path.basename(put_file)

    try:
        # 上传文件
        with open(put_file, "rb") as f:
            result = client.put_object(bucket_name, object_key, content=f)

        server_etag = result.etag.strip('"')  # 获取服务端返回的Etag(通常是文件的MD5)

        return {
            "success": True,
            "local_md5": local_md5,
            "server_etag": server_etag,
            "object_key": object_key,
            "bucket": bucket_name,
        }

    except tos.exceptions.TosServerError as e:
        return {"success": False, "error": f"服务端错误：{e.message}"}
    except Exception as e:
        return {"success": False, "error": f"上传失败：{str(e)}"}


if __name__ == "__main__":

    access_key = os.getenv("TOS_ACCESS_KEY")
    secret_key = os.getenv("TOS_SECRET_KEY")

    endpoint = "tos-cn-shanghai.volces.com"
    region = "cn-shanghai"

    bucket_name = "xorigin"
    date_time = time.strftime("%Y%m%d", time.localtime())
    base_dir = "/backup/database/postgresql"
    db_name = "wiki"

    try:
        client = init_tos_client(access_key, secret_key, endpoint, region)
        put_file = get_file(base_dir, db_name, date_time)
        upload_result = upload_file(bucket_name, put_file, client)

        if upload_result["success"]:
            local_md5 = upload_result["local_md5"]
            server_md5 = upload_result["server_etag"]

            md5_match = local_md5 == server_md5
            if md5_match:
                print(
                    f"MD5校验通过，存储位置：{upload_result['bucket']}/{upload_result['object_key']}"
                )
            else:
                print(f"MD5校验不一致，本地：{local_md5}，服务端：{server_md5}")
        else:
            print(f"文件{put_file}上传失败")
    except Exception as e:
        print(f"文件上传异常：{str(e)}")
