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


def get_file_name(base_dir):
    if not os.path.exists(base_dir):
        print("The backup dir doesn't exist")
        sys.exit(1)
    file_list = os.listdir(base_dir)
    return file_list


def upload_file(file_name, bucket_name, base_dir):
    dir_name = 'bt_backup_qingliang/gitlab'
    object_name = dir_name + '/' + file_name
    put_file_name = base_dir + '/' + file_name

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
        base_dir = "/backup/gitlab"
        bucket_name = 'edu-xmind-1257184986'
        file_list = get_file_name(base_dir)
        for file_name in file_list:
            upload_file(file_name, bucket_name, base_dir)
    except Exception as e:
        print(e)
