#!/bin/bash

PATH=$PATH
export PATH
export TERM=xterm

# 获取进程CPU使用率
function get_cpu() {
  if [ "$PID_LEN" -lt 5 ]; then
    cpu_usage=$(top -bn 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  else
    cpu_usage=$(top -bn 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $9}')
  fi
  echo $cpu_usage
}

# 获取进程内存使用率
function get_mem() {
  if [ "$PID_LEN" -lt 5 ]; then
    mem_usage=$(top -bn 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $11}')
  else
    mem_usage=$(top -bn 1 -p "$PID" |grep "$PID" |awk -F "[ ]+" '{print $10}')
  fi
  echo $mem_usage
}

# 获取主进程的pid号
function get_pid() {
  P_ID=$(ps -ef |grep "$P_NAME" |grep -v "grep" |awk '$3==1{print $2}' |head -1)
  echo "$P_ID"
}

# 发送飞书告警
function send_alert_msg() {
  message=$@
  [ -z "$message" ] && echo "alert message is null, exit" && exit 2
  /usr/bin/env python3 feishu_alert.py "$message"
}

# 获取最近5次的平均值并和阈值比较
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
    send_alert_msg "ip address [118.89.86.95] process [$PID] $metric_name is too high,average value is $avg_5_value"
    return 0
  fi
}

# 获取最近5次的进程数量，小于1则告警
function get_process_num() {
  local Process_Name
  Process_Name=$1
  declare -a Process_Num_Arr=()

  # 获取近5次的进程数量，并放入数组
  for i in {0..4}
  do
    Process_Num=$(ps -ef |grep "$Process_Name" |grep -v "grep" |grep -v "monitor" | wc -l)
    Process_Num_Arr[i]=$Process_Num
    sleep 5
  done
  echo ${Process_Num_Arr[@]}

  # 求数组的和
  sum=0
  for((i=0;i<${#Process_Num_Arr[@]};i++))
  do
    sum=$((sum+Process_Num_Arr[i]))
  done

  if [ $sum -lt 1 ]
  then
    send_alert_msg "服务器[118.89.86.95]上的进程[$Process_Name]异常退出，请及时关注"
    return 0
  fi
}

# 主函数
function main() {
  P_NAME=$1
  metric=$2
  PID=$(get_pid)
  if [ -n "$PID" ]
  then
    PID_LEN=${#PID}
    case $metric in
      cpu)
        get_avg_value cpu
      ;;
      memory)
        get_avg_value memory
      ;;
      process)
        get_process_num "$P_NAME"
      ;;
      *)
        echo "Usage: $0 process_name {cpu|memory|process}"
    esac
  else
    echo "The $P_NAME process is not exist, exit..."
    exit 1
  fi
}
main "$@"
