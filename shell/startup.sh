#!/bin/bash

PATH=$PATH
export PATH

readonly HARBOR_DIR=/home/ubuntu/harbor
readonly NEXUS_DIR=/home/ubuntu/nexus
readonly MIDDLEWARE_DIR=/home/ubuntu/middleware

check_dir() {
  local Dir_name=$1
  if [ ! -d "$Dir_name" ]
  then
    echo "$Dir_name is not exist, exit..."
    exit 1
  fi
}

check_command() {
  Cmd_name="docker-compose"
  which $Cmd_name
  Ret_val=$?
  if [ $Ret_val -ne 0 ]
  then
    echo "Command $Cmd_name is not install, exit..."
    exit 2
  fi
}

start() {
  local array=$1
  check_command
  for dir in ${array[@]}
  do
    check_dir $dir
    cd $dir
    sudo $Cmd_name up -d
    sleep 30
  done
}

main() {
  Dir_array=(HARBOR_DIR NEXUS_DIR MIDDLEWARE_DIR)
  start $Dir_array
}
main
