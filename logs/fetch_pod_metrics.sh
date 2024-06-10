#!/bin/bash

# Function to fetch and print CPU and memory usage for each pod
fetch_pod_metrics() {
  echo "Fetching pod metrics..."
  
  # Get the list of all pods and their metrics
  POD_METRICS=$(kubectl top nodes -n default)

  if [ $? -ne 0 ]; then
    echo "Failed to fetch pod metrics. Please check your Kubernetes configuration."
    exit 1
  fi

  echo -e "POD NAME\tCPU(m)\tCPU(%)"
  echo "$POD_METRICS" | awk 'NR>1 {print $1 "\t" $2 "\t" $3 "\t" $4}'
}

# Fetch pod metrics and display them
# Run the fetch_pod_metrics function every 5 seconds
while true; do
  clear
  fetch_pod_metrics
  sleep 5
done
