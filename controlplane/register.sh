#!/bin/bash

#  ./register.sh /decode-function /decode decode-action [SAMPLE USE]


api_name=$1
path_name=$2
action_name=$3
wsk -i api create $api_name $path_name post $action_name --response-type json



# ./register.sh /increment /increment-by-2  increment-action --response-type=json

# ./register.sh /multiply /multiply-by-2  multiply-action --response-type=json

# ./register.sh /prime /prime-check  prime-check-action --response-type=json  

# ./register.sh /even /even-print  even-print-action --response-type=json 

# ./register.sh /odd /odd-print  odd-print-action --response-type=json 

# ./register.sh /odd-even /odd-even-check  odd-even-action --response-type=json

# ./register.sh /dummy /dummy3  dummy3-action --response-type=json     

# ./register.sh /image-blur-api /image-blur-path image-blur --response-type=json 





