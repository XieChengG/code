#!/bin/bash

readonly UPLOAD_DIR="/home/upload"
readonly NGX_BASE_DIR="/usr/local/openresty/nginx"

DATE=$(date +%Y%m%d%H%M)
SRC_DIR=$UPLOAD_DIR/$DATE

SHEKOU_APP_DIR="$NGX_BASE_DIR/html/urban-design/test"
NANTONG_APP_DIR="$NGX_BASE_DIR/html/urban_planning_NT"

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
  for dir in $2
  do
    app_dir="$1/$dir"
    if [ -d "$app_dir" ]; then
      cd $app_dir
      if [ -d "$BAK_DIR" ]
      then
        rm -fr "$BAK_DIR"
      fi
      mv dist "$BAK_DIR"
      logger INFO "backup $dir successfully"
    else
      logger warn "app dir $app_dir is not exist,continue"
      continue
    fi
  done
  successMsg "backup have done"
}

# mv dist package
function mv_pack() {
  cd $UPLOAD_DIR/$DATE/$1
  a_dirs=(`ls`)
  backup $2 ${a_dirs[@]}
  for a_dir in ${a_dirs[@]}; do
    cd $UPLOAD_DIR/$DATE/$1/$a_dir
    if [ ! -f "dist.zip" ]
    then
      logger error "Error,dist zip file is not exist,exit"
      exit 2
    fi
    unzip dist.zip >/dev/null
    mv dist $2/$a_dir/
    logger INFO "deploy $a_dir have done"
    sleep 3
  done
}

# deploy
function deploy() {
  logger INFO "deploy beginning..."
  if [ -d "$UPLOAD_DIR/$DATE" ]
  then
    cd "$UPLOAD_DIR/$DATE"
    project_names=(`ls`)
    for name in ${project_names[@]}
    do
      logger info "----deploy project ${name}----"
      case $name in
        shekou)
          mv_pack $name $SHEKOU_APP_DIR
          ;;
        nantong)
          mv_pack $name $NANTONG_APP_DIR
          ;;
        *)
          logger error "Error, project name incorrect, exit"
          exit 3
      esac
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
    deploy
  elif [ "$action" == "install" ]; then
    deploy
  fi
}

main $@
