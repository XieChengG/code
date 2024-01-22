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
  BAK_DIR="dist-backup"
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
      logger error "app dir $app_dir is not exist,exit"
      exit 1
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

# rollback frontend app
function rollback() {
  local p_name=$1
  local a_name=$2
  if [ "$p_name" == "nantong" ]; then
    a_dir=$NANTONG_APP_DIR/$a_name
  elif [ "$p_name" == "shekou" ]; then
    a_dir=$SHEKOU_APP_DIR/$a_name
  fi

  if [ ! -d "$a_dir" ]; then
    logger error "error, app dir $a_dir is not exist, exit"
    exit 1
  fi

  cd $a_dir
  if [ -d "$BAK_DIR" ]; then
    mv dist dist-redo
    mv $BAK_DIR dist
    logger info "rollback $p_name $a_name successfully"
  else
    logger error "error, backup dir is not exist, exit"
    exit 1
  fi
}

# main function
function main() {
  action=$1
  if [ "$action" == "" ]; then
    deploy
  elif [ "$action" == "install" ]; then
    deploy
  elif [ "$action" == "rollback" ]; then
    rollback $2 $3
  fi
}

main $@
