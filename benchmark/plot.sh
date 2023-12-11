#!/usr/bin/gnuplot  
  
set size ratio 0.4
set terminal png
set output 'gpu_usage.png'
set title 'GPU Utilization Over Time'
set xlabel 'Time (s)'
set ylabel 'Utilization (%)'
plot 'gpu_usage.txt' using ($0*0.1):1 title 'GPU Utilization' with lines  
