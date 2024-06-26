#!/bin/bash

function get_cpu() {
  if [ "$PID_LEN" -lt 5 ]; then
    cpu_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  else
    cpu_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $9}')
  fi
  echo $cpu_usage
  local value=0.1
  local result
  result=$(echo "$cpu_usage > $value" | bc)
  if [ $result -eq 1 ]; then
    send_alert_msg "进程 $PID CPU使用率高，值为 $cpu_usage，请及时关注"
  fi
}

function get_mem() {
  if [ "$PID_LEN" -lt 5 ]; then
    mem_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $11}')
  else
    mem_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  fi
  echo $mem_usage
  local value=1.2
  local result
  result=$(echo "$mem_usage > $value" | bc)
  if [ $result -eq 1 ]; then
    send_alert_msg "进程 $PID 内存使用率高，值为 $mem_usage，请及时关注"
  fi
}

function get_pid() {
  P_ID=$(ps -ef |grep "$P_NAME" |grep -v "grep" |awk '$3==1{print $2}' |head -1)
  if [ -z "$P_ID" ]; then
    echo "The process $P_NAME is not exist,exit"
    exit 1
  fi
  echo $P_ID
}

function send_alert_msg() {
  message=$@
  [ -z "$message" ] && echo "alert message is null, exit" && exit 2
  /usr/bin/env python3 feishu_alert.py "$message"
}

function main() {
  P_NAME=$1
  metric=$2
  PID=$(get_pid)
  PID_LEN=${#PID}
  case $metric in
    cpu)
      get_cpu
    ;;
    memory)
      get_mem
    ;;
    *)
      echo "Usage: $0 process_name {cpu|memory}"
  esac
}
main $@
