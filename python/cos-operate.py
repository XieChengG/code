#!/usr/bin/env python3
import sys
import os
import time
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = 'AKIDylJaaJlwrVt1tWsynLccLo1xc190atxl'
secret_key = ''
token = None
region = 'ap-shanghai'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)
client = CosS3Client(config)


def get_file_name(base_dir, backup_time):
    bak_dir = os.path.join(base_dir, backup_time)
    if not os.path.exists(bak_dir):
        print("The backup dir doesn't exist")
        sys.exit(1)
    file_list = os.listdir(bak_dir)
    return file_list


def upload_file(file_name, bucket_name, base_dir, backup_time):
    dir_name = 'bt_backup_qingliang/database/mongodb'
    object_name = dir_name + '/' + file_name
    put_file_name = os.path.join(base_dir, backup_time) + '/' + file_name

    with open(put_file_name, 'rb') as f:
        response = client.put_object(
            Bucket=bucket_name,
            Body=f,
            Key=object_name,
            EnableMD5=True,
            StorageClass='STANDARD',
            ContentType='application/x-tar'
        )
    print(response['ETag'])


if __name__ == '__main__':
    try:
        base_dir = "/backup/database/mongodb"
        bucket_name = 'edu-xmind-1257184986'
        backup_time = time.strftime("%Y%m%d", time.localtime())
        file_list = get_file_name(base_dir, backup_time)
        for file_name in file_list:
            upload_file(file_name, bucket_name, base_dir, backup_time)
    except Exception as e:
        print(e)
