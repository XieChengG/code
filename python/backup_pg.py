#!/usr/bin/env python3

import os
import time
import psycopg2
import logging
import sys


class BackupPgsql(object):
    # 构造函数
    def __init__(self):
        self.db_host = '127.0.0.1'
        self.db_port = 5432
        self.db_user = 'postgres'
        self.db_pass = "Xzkj123456"
        self.db_default = "postgres"
        self.backup_path = "/backup/pgsql"
        self.backup_time = time.strftime("%Y%m%d")
        self.databases = []

    # 检测备份路径是否存在
    def _check_backup_path(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            return True
        else:
            return True

    # 获取所有的数据库
    def _get_databases(self, log_obj):
        try:
            connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,
                                          password=self.db_pass, database=self.db_default)
            print(connection)
            if not connection:
                raise CustomException("Database connection failed...")  # 抛出异常
        except CustomException as e:
            # 打印日志，并写入文件
            log_obj.error(e.msg)
        else:
            cursor = connection.cursor()
            cursor.execute("select datname from pg_database where datname not in ('template0','template1','postgres')")
            rows = cursor.fetchall()
            for row in rows:
                self.databases.append(row[0])
            connection.close()
            return self.databases

    # 备份单个数据库数据
    def backup_database(self, log_obj):
        databases = self._get_databases(log_obj)
        try:
            if self._check_backup_path():
                for database in databases:
                    stdout = os.popen(
                        "su - postgres -c '/www/server/pgsql/bin/pg_dump --create -d {0} |gzip >{2}/{0}_{1}.sql.gz'".format(
                            database,
                            self.backup_time,
                            self.backup_path))
                    print(stdout.read())

        except BaseException as e:
            log_obj.error(e)
        else:
            for database in databases:
                backup_file = "{0}/{1}_{2}.sql.gz".format(self.backup_path, database, self.backup_time)
                if os.path.exists(backup_file) and os.stat(backup_file).st_size > 0:
                    log_obj.info("Backup database {database} successfully".format(database=database))
                else:
                    log_obj.error("Backup database {database} failed".format(database=database))

    # 日志记录
    def logger(self):
        # 创建一个logger日志记录器
        logger_name = "pg_backup"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # 创建stream handler处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 创建file handler处理器
        log_path = "/var/log/pgsql/"
        log_file_name = "pg_backup.log"
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        fh = logging.FileHandler("%s/%s" % (log_path, log_file_name))
        fh.setLevel(logging.INFO)

        # 创建一个格式化器
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        datefmt = "%a %d %b %Y %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)

        # 添加formatter到handler处理器
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # 把handler添加到logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger


class CustomException(Exception):
    def __init__(self, msg):
        super(CustomException, self).__init__(msg)  # 重构父类的构造方法
        self.msg = msg

    def __str__(self):
        return self.msg


if __name__ == '__main__':
    backup_pgsql = BackupPgsql()
    log_obj = backup_pgsql.logger()
    backup_pgsql.backup_database(log_obj)
