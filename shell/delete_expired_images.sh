#!/bin/bash

PATH=$PATH
export PATH

export TERM=xterm


function get_image_arr() {
    image_arr=(`sudo docker images -q`)
    for ((i=0;i<${#image_arr[@]};i++));
    do
      image=${image_arr[i]}
      has_xzkj_str=`sudo docker images |grep $image |grep -c "xzkj"`
      has_run_image=`sudo docker ps |grep -c $image`
      if [ $has_xzkj_str -gt 0 -a $has_run_image -eq 0 ]; then
        sudo docker rmi -f $image
        RETVAL=$?
        if [ $RETVAL -ne 0 ]
        then
          echo "Error, exit..."
          exit 1
        else
          echo "image $image is deleted..."
        fi
        sleep 3
      fi

    done
}

get_image_arr
