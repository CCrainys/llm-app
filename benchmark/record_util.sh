#!/bin/bash  

rm gpu_usage.txt
cnt=100
while [ $cnt -ne 0 ]; do
    nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | awk '{print $1}' >> gpu_usage.txt
    sleep 0.5
    cnt=$((cnt-1))
done
