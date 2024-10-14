#!/bin/bash

PATH=$PATH
export PATH
export TERM=xterm

readonly MONGO_USER='root'
readonly MONGO_PWD='xzkj@123'
readonly MONGO_HOST='127.0.0.1'
readonly MONGO_PORT=27017

BASE_DIR=/backup/database/mongodb
BAK_TIME=$(date +%Y%m%d)
BAK_DIR=${BASE_DIR}/$BAK_TIME

# 检测备份目录是否存在
function Check_dir() {
  if [ ! -d "$BAK_DIR" ]
  then
    sudo mkdir -p "$BAK_DIR"
    RETVAL=$?
    if [ $RETVAL -ne 0 ]
    then
      logger error "创建备份目录[$BAK_DIR]失败，请重试"
      exit 3
    fi
    cd "$BAK_DIR"
  else
    cd "$BAK_DIR"
  fi
}

# 检测是否有MongoDB进程运行
function Check_process() {
  local process_num
  process_num=$(netstat -lntup |grep $MONGO_PORT |wc -l)
  if [ $process_num -eq 0 ]; then
    logger error "MongoDB 进程不存在，脚本退出"
    exit 1
  fi
}

# 打印日志
function logger() {
  LOG_HOME="/tmp/backup"
  postfix=`date +'%Y-%m'`
  LOG_FILE=$LOG_HOME/backup.log.$postfix

  timestamp=`date +'%Y-%m-%d %H:%M:%S %z'`
  level=$1
  shift 1
  message=$@
  case $level in
    info|warn|error|debug|INFO|WARN|ERROR|DEBUG)
      level=`echo $level|tr 'a-z' 'A-Z'`
      ;;
    *)
      level=ERROR
      message="log format error, missing parameters"
  esac
  echo "$timestamp|$level|$message" 2>&1 |tee -a $LOG_FILE
}

# 对MongoDB进行全备份
function Mongo_all_backup() {
  sudo mongodump -u $MONGO_USER -p $MONGO_PWD -h $MONGO_HOST --port $MONGO_PORT --authenticationDatabase admin -o $BAK_DIR
  RETVAL=$?
  if [ $RETVAL -ne 0 ]
  then
    logger ERROR "MongoDB 备份命令执行失败，请重试"
    exit 2
  fi
  sleep 5
}

# 检测备份文件的有效性
function Check_backup_file() {
  databases=(`ls`)
  for db in ${databases[@]}
  do
    if [ "$(ls -A $db)" ]; then
      # 数据库目录不为空
      cd $db
      file_array=(`ls`)
      for file in ${file_array[@]}
      do
        file_size=$(stat -c %s $file)
        if [ $file_size -gt 0 ]; then
          logger info "备份数据库[$db]成功"
          break
        fi
      done
      cd ..
    else
      logger warn "备份数据库[$db]为空，请检查是否正常"
      cd ..
    fi
  done
}

# 删除过期的备份数据，只保留最近3天的备份
function Delete_expired_file() {
  cd $BASE_DIR
  find ./ -type d -mtime +3 -exec rm -fr {} \;
}

# main
function main() {
  Check_dir
  Check_process
  Mongo_all_backup
  Check_backup_file
  Delete_expired_file
}
main
