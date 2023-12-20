#!/bin/bash

cd /home/faasapp/Desktop/anubhav/function_modules/text-sentiment-analysis/url_to_summary
wsk -i action create fetch_sentences --docker 10.129.28.219:5000/text-sentiment-analysis data_processing.py --web=true --timeout=420000 -m 128
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /fetch-sentences-api /fetch-sentences-path fetch_sentences --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/text-sentiment-analysis/calculate_text_sentiment
wsk -i action create calculate_sentiment --docker 10.129.28.219:5000/text-sentiment-analysis sentiment.py --web=true --timeout=420000 -m 128
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /calculate-sentiment-api /calculate-sentiment-path calculate_sentiment --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/text-sentiment-analysis/create_sentiment_report
wsk -i action create create_sentiment_report --docker 10.129.28.219:5000/text-sentiment-analysis sentiment_report.py --web=true --timeout=420000 -m 128
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /create_sentiment_report-api /create_sentiment_report-path create_sentiment_report --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/toonify/decode-function
wsk -i action create decode-function --docker 10.129.28.219:5000/decode-function-image --web=true --timeout=420000 -m 512
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /decode-function /decode decode-function --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/image-blur
wsk -i action create image-blur --docker 10.129.28.219:5000/image-processing blur.py --web=true --timeout=600000 -m 512
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-blur-api /image-blur-path image-blur --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/image-thresholding
wsk -i action create image-thresholding --docker 10.129.28.219:5000/image-processing threshold.py --web=true --timeout=600000 -m 256
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-thresholding-api /image-thresholding-path image-thresholding --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/image-rotate
wsk -i action create image-rotate --docker 10.129.28.219:5000/image-processing rotate.py --web=true --timeout=600000 -m 512
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-rotate-api /image-rotate-path image-rotate --response-type=json


cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/image-denoise
wsk -i action create image-denoise --docker 10.129.28.219:5000/image-processing denoise.py --web=true --timeout=420000
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-denoise-api /image-denoise-path image-denoise --response-type=json


cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/image-histogram
wsk -i action create image-histogram --docker 10.129.28.219:5000/image-processing img_hist.py --web=true --timeout=600000 -m 512
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-hist-api /image-hist-path image-histogram --response-type=json


cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/merger
wsk -i action create merger-function --docker 10.129.28.219:5000/image-processing merge.py --web=true --timeout=600000
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-merge-api /image-merge-path  merger-function --response-type=json

cd /home/faasapp/Desktop/anubhav/function_modules/image_processing/merger
wsk -i action create merger-function-1 --docker 10.129.28.219:5000/image-processing merge_2.py --web=true --timeout=600000 
cd /home/faasapp/Desktop/anubhav/controlplane
./register.sh /image-merge-1-api /image-merge-1-path  merger-function-1 --response-type=json

