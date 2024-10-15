#!/usr/bin/env python3

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

token = None
region = 'ap-shanghai'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)
client = CosS3Client(config)

dir_name = 'bt_backup_qingliang/database/mongodb'
file_name = 'admin_20241014.tar.gz'
object_name = dir_name + '/' + file_name

with open('../admin_20241014.tar.gz', 'rb') as f:
    response = client.put_object(
        Bucket='edu-xmind-1257184986',
        Body=f,
        Key=object_name,
        EnableMD5=True,
        StorageClass='STANDARD',
        ContentType='application/x-tar'
    )
print(response['ETag'])
