# FROM openwhisk/python3action

# # RUN apk --update add --no-cache g++ lapack-dev gfortran openssl ca-certificates py-openssl jpeg-dev zlib-dev libjpeg

# RUN apk --update add --virtual build-dependencies g++ openssl ca-certificates py-openssl lapack-dev gfortran openssl python-dev py-pip py-openssl build-base \
# && apk add jpeg-dev zlib-dev libjpeg  \
# && pip install --upgrade pip 

# RUN pip install Pillow==6.2.2

# RUN pip install textblob nltk newspaper3k

# RUN pip install pandas 

# RUN python -m textblob.download_corpora

# RUN pip install redis

# RUN pip install flask

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed dependencies specified in requirements.txt
# (You may not need this step if your script is self-contained)
# RUN pip install --no-cache-dir -r requirements.txt


RUN pip install textblob nltk newspaper3k

RUN pip install pandas 

RUN python -m textblob.download_corpora

RUN pip install redis

RUN pip install flask

RUN pip install requests

RUN pip install python-dotenv

RUN pip install minio

CMD ["python", "sentiment.py"]

