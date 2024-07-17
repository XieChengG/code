#!/usr/bin/env python3

import os
import time
import psycopg2
import logging
import sys
import datetime


class BackupPgsql(object):
    # 构造函数
    def __init__(self):
        self.db_host = '127.0.0.1'
        self.db_port = 5432
        self.db_user = 'postgres'
        self.db_pass = "Xzkj123456"
        self.db_default = "postgres"
        self.backup_time = time.strftime("%Y%m%d")
        self.backup_path = "/backup/pgsql/%s" % self.backup_time
        self.databases = []

    # 检测备份路径是否存在
    def _check_backup_path(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            os.chown(self.backup_path, 1003, 1003)
            return True
        else:
            return True

    # 获取所有的数据库
    def _get_databases(self, log_obj):
        try:
            connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,
                                          password=self.db_pass, database=self.db_default)
        except BaseException as e:
            # 打印日志，并写入文件
            log_obj.error(e)
        else:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "select datname from pg_database where datname not in ('template0','template1','postgres')")
                rows = cursor.fetchall()
                for row in rows:
                    self.databases.append(row[0])
                connection.close()
                return self.databases
            except BaseException as e:
                log_obj.error(e)

    # 备份单个数据库数据
    def backup_database(self, log_obj):
        databases = self._get_databases(log_obj)
        if not databases:
            raise CustomException(log_obj.error("No databases found"))
        try:
            if self._check_backup_path():
                for database in databases:
                    stdout = os.popen(
                        "su - postgres -c '/www/server/pgsql/bin/pg_dump --create -d {0} |gzip >{2}/{0}_{1}.sql.gz'".format(
                            database,
                            self.backup_time,
                            self.backup_path))
                    time.sleep(10)
                    print(stdout.read())

        except BaseException as e:
            log_obj.error(e)
        else:
            for database in databases:
                backup_file = "{0}/{1}_{2}.sql.gz".format(self.backup_path, database, self.backup_time)
                if os.path.exists(backup_file) and os.stat(backup_file).st_size > 20:
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
        fmt = "%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s"
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


class DeleteFiles(object):
    def __init__(self, path):
        self.path = path
        self.current_time = datetime.datetime.now()  # 获取当前时间
        self.offset = datetime.timedelta(days=-3)
        self.before_time = self.current_time + self.offset  # 获取前3天的时间
        self.before_timestamp = time.mktime(self.before_time.timetuple())  # 转换为时间戳格式

    def delete_files(self, log_obj):
        path_list = [self.path]
        try:
            while path_list:
                path = path_list.pop()
                file_list = os.listdir(path)
                for file in file_list:
                    file_path = os.path.join(path, file)  # 拼接成绝对路径
                    if os.path.isfile(file_path):  # 如果是普通文件
                        if os.path.getctime(file_path) < self.before_timestamp:  # 如果是3天前的文件则删除
                            os.remove(file_path)
                            log_obj.info("Delete file {0}".format(file_path))
                            if not os.listdir(os.path.dirname(file_path)):  # 文件删完了，最后删目录
                                os.removedirs(os.path.dirname(file_path))
                                log_obj.info("Delete directory {0}".format(os.path.dirname(file_path)))
                    elif os.path.isdir(file_path):
                        if not os.listdir(file_path):  # 如果是空目录
                            os.removedirs(file_path)
                            log_obj.info("Delete null directory {0}".format(file_path))
                        else:
                            path_list.append(file_path)  # 如果目录不为空，则添加到path列表，再次循环
            return True
        except BaseException as e:
            log_obj.error(e)
            return False


if __name__ == '__main__':
    try:
        backup_pgsql = BackupPgsql()
        log_obj = backup_pgsql.logger()
        backup_pgsql.backup_database(log_obj)  # 备份数据库
        delete_files = DeleteFiles(backup_pgsql.backup_path[:backup_pgsql.backup_path.rfind("/")])
        res = delete_files.delete_files(log_obj)
        if not res:
            log_obj.error("Delete files failed!")
    except BaseException as e:
        print(e)
        sys.exit(1)
