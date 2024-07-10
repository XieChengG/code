#!/usr/bin/env python3

import os
import time
import psycopg2


class BackupPgsql(object):
    # 构造函数
    def __init__(self):
        self.db_host = '127.0.0.1'
        self.db_port = 5432
        self.db_user = 'postgres'
        self.db_pass = ""
        self.db_default = "postgres"
        self.backup_path = "/backup/pgsql"
        self.backup_time = time.strftime("%Y%m%d")
        self.databases = []

    # 检测备份路径是否存在
    def _check_backup_path(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            return True

    # 获取所有的数据库
    def _get_databases(self):
        try:
            connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,
                                          password=self.db_pass, database=self.db_default)
        except BaseException as e:
            # 此处应打印日志，并写入文件
            print(e)
        else:
            cursor = connection.cursor()
            cursor.execute("select datname from pg_database where datname not in ('template0','template1','postgres',)")
            rows = cursor.fetchall()
            for row in rows:
                self.databases.append(row[0])
            connection.close()
            return self.databases

    # 备份单个数据库数据
    def backup_database(self):
        try:
            if self._check_backup_path():
                databases = self._get_databases()
                for database in databases:
                    os.system("/www/server/pgsql/bin/pg_dump --create -d {0} |gzip >{2}/{0}_{1}.sql.gz".format(database,
                                                                                                            self.backup_time,
                                                                                                            self.backup_path))
        except BaseException as e:
            # 此处写日志
            print(e)
        else:
            return True


if __name__ == '__main__':
    backup_pgsql = BackupPgsql()
    backup_result = backup_pgsql.backup_database()
    if backup_result:
        print("Backup successful")
