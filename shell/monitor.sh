#!/bin/bash

function get_cpu() {
  if [ "$PID_LEN" -lt 5 ]; then
    cpu_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  else
    cpu_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $9}')
  fi
  echo $cpu_usage
}

function get_mem() {
  if [ "$PID_LEN" -lt 5 ]; then
    mem_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $11}')
  else
    mem_usage=$(top -n 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  fi
  echo $mem_usage
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

function get_avg_value() {
  metric_name=$1
  declare -a value_array=()  # 定义空数组
  for i in {0..4}; do  # 获取近5秒的监控值
    if [ "$metric_name" == "cpu" ]; then
      value_array[i]=$(get_cpu)
    elif [ "$metric_name" == "memory" ]; then
      value_array[i]=$(get_mem)
    fi
    sleep 5
  done

  sum=0
  for ((i=0;i<${#value_array[@]};i++))
  do
    sum=$(echo "$sum+${value_array[i]}" | bc)
  done
  num=${#value_array[@]}
  avg_5_value=$(echo "$sum/$num" | bc)

  local value=90.0
  local result
  result=$(echo "$avg_5_value > $value" | bc)
  if [ $result -eq 1 ]
  then
    send_alert_msg "process $PID $metric_name is too high,average value is $avg_5_value"
    return 0
  fi
}

function main() {
  P_NAME=$1
  metric=$2
  PID=$(get_pid)
  PID_LEN=${#PID}
  case $metric in
    cpu)
      get_avg_value cpu
    ;;
    memory)
      get_avg_value memory
    ;;
    *)
      echo "Usage: $0 process_name {cpu|memory}"
  esac
}
main $@
