#!/bin/bash

# Function to send HTTP request using curl
send_request() {
    url=$1
    for i in {1..100}; do
        curl -d '{"quantity": 999}' -H "Content-Type: application/json" -X POST "$url" &
    done
}

# Sending requests to different endpoints in parallel
send_request "http://10.129.28.219:5030/run/fill_a_glass_of_water" 
send_request "http://10.129.28.219:5030/run/fill_a_glass_of_water_1" 
send_request "http://10.129.28.219:5030/run/fill_a_glass_of_water_2" 

# Wait for all background processes to finish
wait

echo "All requests sent successfully."


