#!/bin/bash
wsk -i api list | awk -F " " '{if(NR>2)print $1,$4}' > action_url.txt
