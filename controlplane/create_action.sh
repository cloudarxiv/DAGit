#!/bin/bash

function_dir_name=$1
docker_image_name=$2
function_name=$3

cd $function_dir_name

chmod -R 777 ./

wsk -i action create $function_name --docker $docker_image_name --web=true --timeout=300000

