#!/bin/bash  

rm gpu_usage.txt
cnt=500
while [ $cnt -ne 0 ]; do
    nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | awk '{print $1}' >> gpu_usage.txt
    sleep 0.1
    cnt=$((cnt-1))
done
