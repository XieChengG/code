#!/bin/bash

PATH=$PATH
export PATH
export TERM=xterm

# 获取进程CPU使用率
function get_cpu() {
  declare -a cpu_value_arr=()
  for ((i=0;i<${#pids[@]};i++))
  do
    local pid
    pid=${pids[i]}
    local pid_len
    pid_len=${#pid}
    if [ "$pid_len" -lt 5 ]; then
      cpu_usage=$(top -bn 1 -p "$pid" |grep "$pid" |awk -F "[ ]+" '{print $10}')
    else
      cpu_usage=$(top -bn 1 -p "$pid" |grep "$pid" |awk -F "[ ]+" '{print $9}')
    fi
    cpu_value_arr[i]=$cpu_usage
  done

  local cpu_value_sum=0
  for ((i=0;i<${#cpu_value_arr[@]};i++))
  do
    cpu_value_sum=$(echo "$cpu_value_sum+${cpu_value_arr[i]}" | bc)
  done

  echo $cpu_value_sum
}

# 获取进程内存使用率
function get_mem() {
  declare -a mem_value_arr=()
  for ((i=0;i<${#pids[@]};i++))
  do
    local pid
    pid=${pids[i]}
    local pid_len
    pid_len=${#pid}
    if [ "$pid_len" -lt 5 ]; then
      mem_usage=$(top -bn 1 -p "$pid" |grep "$pid" |awk -F "[ ]+" '{print $11}')
    else
      mem_usage=$(top -bn 1 -p "$pid" |grep "$pid" |awk -F "[ ]+" '{print $10}')
    fi
    mem_value_arr[i]=$mem_usage
  done

  local mem_value_sum=0
  for ((i=0;i<${#mem_value_arr[@]};i++))
  do
    mem_value_sum=$(echo "$mem_value_sum+${mem_value_arr[i]}" | bc)
  done

  echo $mem_value_sum
}

# 获取主进程的pid号
function get_pid() {
  pids=($(ps -ef |grep "$P_NAME" |grep -v "grep" |grep -v "monitor" |awk '{print $2}'))
  echo ${pids[@]}
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
  pids=($(get_pid))
  if [ "${#pids[@]}" -ne 0 ]
  then
    declare -a value_array=()  # 定义空数组
    for i in {0..4}; do  # 获取近5秒的监控值
      if [ "$metric_name" == "cpu" ]; then
        value_array[i]=$(get_cpu)
      elif [ "$metric_name" == "memory" ]; then
        value_array[i]=$(get_mem)
      fi
      sleep 5
    done
    echo ${value_array[@]}

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
      send_alert_msg "ip address [118.89.86.95] process [$P_NAME] $metric_name is too high,average value is $avg_5_value"
      return 0
    fi
  else
    echo "The $P_NAME process is not exists, exit"
    exit 1
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
  for ((i=0;i<${#Process_Num_Arr[@]};i++))
  do
    sum=$((sum+Process_Num_Arr[i]))
  done

  if [ $sum -lt 1 ]
  then
    send_alert_msg "服务器[118.89.86.95]上的进程[$Process_Name]异常退出，请及时关注"
    return 0
  fi
}

# web监测，检测站点是否能正常访问
function web_check() {
  local domain_name
  domain_name="$1"
  [ -z "$domain_name" ] && echo "请输入域名参数" && exit 1
  declare -a code_arr=()
  for i in {0..9}
  do
    resp_code=$(curl -sI 'http://'$domain_name'' |grep "HTTP" |awk '{print $2}')
    if [ "$resp_code" != "200" -a "$resp_code" != "301" -a "$resp_code" != "302" -a "$resp_code" != "304" ]
    then
      code_arr[i]=$resp_code
    fi
    sleep 10
  done

  if [ ${#code_arr[@]} -gt 5 ]
  then
    send_alert_msg "$domain_name 网站不可访问，请及时关注"
    return 1
  else
    return 0
  fi
}

# 主函数
function main() {
  P_NAME=$1
  metric=$2

  if [ "$metric" == "cpu" ]; then
    get_avg_value cpu
  elif [ "$metric" == "memory" ]; then
    get_avg_value memory
  elif [ "$metric" == "process" ]; then
    get_process_num "$P_NAME"
  elif [[ "$P_NAME" =~ ^([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+[a-zA-Z0-9]{2,}$ ]]; then
    web_check "$P_NAME"
  else
    echo "Usage: $0 process_name {cpu|memory|process}"
  fi
}
main "$@"
