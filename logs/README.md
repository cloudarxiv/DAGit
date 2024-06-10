<h1> Load Testing and Recording Metrics </h1>

This document outlines the process for load testing mixed workloads using Apache Benchmark and recording various metrics including throughput, response time, and cluster-level and priority-based metrics. It provides instructions for running the load generator, fetching cluster-level metrics, and recording priority-based metrics for both static and dynamic priorities.

<h2> Workload 1 </h2>

> Trigger Name : text_sentiment_analysis_trigger  
> Functions: fetch-sentences, calculate-sentiment, create-sentiment-report  
> Primitives used: Serial & Multi-Stage Input Output

<h2> Workload 2 </h2>

> Trigger Name : filling_glass_of_water  
> Functions: check-if-full, add-water, glass-full  
> Primitives: Serial, Loop & Conditional

For mixed workloads --- these two were run in parallel with apache benchmark and requests arrived at the order in which requests were completed. It followed no particular order. 


<h2> Running Load Generator with Apache Benchmark </h2>

To run an Apache Benchmark (ab) test with the specified parameters, use the following command:

For each iteration, keep total requests fixed and change the level of concurrency to identify saturation. For running mixed workload, run the below "ab" commands as background processes.

```bash

ab -k -n 10000 -c 50 -s 600 -p request1.json -T application/json http://10.129.28.219/run/fill_a_glass_of_water &
ab -k -n 10000 -c 50 -s 600 -p request.json -T application/json http://10.129.28.219/run/text_sentiment_analysis_trigger &


```

<h3>Explanation of Parameters:</h3>

> -k: Use HTTP KeepAlive feature  
> -n 100: Number of requests to perform  
> -c 20: Number of multiple requests to make at a time  
> -s 600: Maximum number of seconds to wait for a response  
> -p request1.json: File containing the data to POST  
> -T application/json: Content-type header to use for POST data

<h3>Measure Outputs</h3>

After running the benchmark, important metrics to observe include:

* Requests per second (Throughput)
* Mean response time
* Total time taken for the tests
* Percentage of requests served within a certain time


<h2> Recording Cluster Level Metrics </h2>

* Step 1: Start Apache Benchmark Load Generator : Start the load generation using the Apache Benchmark command provided above.

* Step 2: Run fetch_node_metrics.py : Run the script fetch_node_metrics.py to fetch node-level metrics every 5 seconds. This script will capture metrics such as CPU usage,memory usage for each node in the cluster.

The CSV file containing the metrics information for each node will be generated and saved (wokrer_metrics_replica_2.csv) . Repeat for each replica.


<h2> Recording Priority-Based Metrics </h2>

Running the Load Generator: To record priority level metrics, run the ./loadgen.sh script (which runs 3 triggers of 3 different priorities) and monitor the dagit.logs for the necessary metrics.

Calculating Metrics from Logs: 

Read from dagit.logs to calculate:

* Queue delay
* Number of requests processed per time slot

## Static Priority ##

For static priority:

1. Run the workflow with initial weights.
2. Stop the server.
3. Update the weights.
4. Restart the server with the updated weights.


## Dynamic Priority ##

For dynamic priority:

1. Run ./loadgen.sh for the first 30 seconds with initial weights.
2. Change the weight proportion on the fly parallely (maybe in a different terminal)
3. Run for another 30 seconds, and continue this process.
4. Observe the logs in dagit.logs.


Here is the example to update weights on the fly: 

```bash

curl -X POST -H "Content-Type: application/json" -d '{"gold": 5, "silver": 3, "bronze": 1}' http://10.129.28.219:5030/update_weights

```