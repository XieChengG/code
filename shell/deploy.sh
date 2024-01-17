#!/bin/bash

readonly UPLOAD_DIR="/home/upload"
readonly NGX_BASE_DIR="/usr/local/openresty/nginx"

DATE=$(date +%Y%m%d%H%M)
SRC_DIR=$UPLOAD_DIR/$DATE

APP_DIR="$NGX_BASE_DIR/html/urban-design/test"

# message output
function successMsg() {
    echo "$@"
}

function failureMsg() {
    echo "$@"
}

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

# backup
function backup() {
  local BAK_DIR="dist-backup"
  for dir in web client mobile
  do
    cd $APP_DIR/$dir
    if [ -d "$BAK_DIR" ]
    then
      rm -fr "$BAK_DIR"
    fi
    mv dist "$BAK_DIR"
    logger INFO "backup $dir successfully"
  done
  successMsg "backup have done"
}

# deploy
function deploy() {
  logger INFO "deploy beginning..."
  if [ -d "$UPLOAD_DIR/$DATE" ]
  then
    cd "$UPLOAD_DIR/$DATE"
    SUB_DIRS=(`ls`)
    for sub_dir in ${SUB_DIRS[@]}
    do
      cd $UPLOAD_DIR/$DATE/$sub_dir
      if [ ! -f "dist.zip" ]
      then
        logger error "Error,dist zip file is not exist,exit"
        exit 2
      fi
      unzip dist.zip >/dev/null
      mv dist $APP_DIR/$sub_dir/
      logger INFO "deploy $sub_dir have done"
      sleep 3
    done
  else
    logger error "deploy dir is not exist, exit"
    exit 1
  fi
  logger INFO "deploy all app successfully..."
}

# main function
function main() {
  action=$1
  if [ "$action" == "" ]; then
    backup
    deploy
  elif [ "$action" == "install" ]; then
    backup
    deploy
  fi
}

main $@
