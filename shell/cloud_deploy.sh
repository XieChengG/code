#!/bin/bash

CURRENT_DIR=`dirname $0`
CURRENT_TIMESTAMP=$(date +%s)
BAK_DIR="dist-backup-$(date +%Y%m%d%H%M)"
PKG_NAME='dist.zip'


# logger of deploy "timestamp|level|message"
function logger() {
    LOG_HOME="/tmp/deploy"
    postfix=`date +'%Y-%m'`
    LOG_FILE=$LOG_HOME/deploy.log.$postfix

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
	      message="logger format error, missing parameters"
    esac
    echo "$timestamp|$level|$message" 2>&1 | tee -a $LOG_FILE
}

# update deploy package
function change_file() {
  cd $1
  mkdir $BAK_DIR
  mv ./* ${BAK_DIR}/ 2>/dev/null
  mv ${BAK_DIR}/$PKG_NAME ./
  mv ${BAK_DIR}/dist-backup-* ./
  unzip $PKG_NAME >/dev/null
  rm -f $PKG_NAME
  logger info "deploy $1 successfully"
}

# monitor directory changes
function monitor_pkg() {
  cd $CURRENT_DIR
  sub_dirs=(`ls`)
  for dir in ${sub_dirs[@]}; do
    dir_acc_timestamp=`stat -c %X $dir`
    timestamp_diff_val=$((CURRENT_TIMESTAMP-dir_acc_timestamp))
    if [ $timestamp_diff_val -lt 1200 ]; then
      ls ${dir}/$PKG_NAME >/dev/null 2>&1
      ret_val=$?
      if [ $ret_val -eq 0 ]; then
        change_file $dir
        break
      fi
    fi
  done
}
monitor_pkg
