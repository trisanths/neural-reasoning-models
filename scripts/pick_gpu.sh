#!/bin/bash
# Print the index of the GPU with the least memory in use, ignoring any whose
# utilization is high. Never signals another process; it only reads.
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader,nounits |
  awk -F', ' '$2 < 60 {print $3, $1}' | sort -n | head -1 | awk '{print $2}'
