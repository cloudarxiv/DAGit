FROM openwhisk/python3action

RUN apk --update add --no-cache g++ lapack-dev gfortran openssl ca-certificates py-openssl jpeg-dev zlib-dev libjpeg
RUN pip install requests redis boto3

