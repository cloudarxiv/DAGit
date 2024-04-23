FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY . .

# RUN pip install --no-cache-dir -r requirements.txt


RUN pip install pandas 

RUN pip install redis

RUN pip install flask

RUN pip install requests

CMD ["python", "sentiment_report.py"]
