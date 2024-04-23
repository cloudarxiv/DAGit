# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed dependencies specified in requirements.txt
# (You may not need this step if your script is self-contained)
# RUN pip install --no-cache-dir -r requirements.txt


RUN pip install Pillow

RUN pip install textblob nltk newspaper3k

RUN pip install pandas 

RUN python -m textblob.download_corpora

RUN pip install redis

RUN pip install flask

RUN pip install requests

RUN pip install lxml_html_clean

CMD ["python", "data_processing.py"]
