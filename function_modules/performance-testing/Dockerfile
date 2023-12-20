# Dockerfile for Python whisk docker action
FROM openwhisk/dockerskeleton

ENV FLASK_PROXY_PORT 8080

# Install our action's Python dependencies
ADD requirements.txt /action/requirements.txt


RUN apk --update add python py-pip openssl ca-certificates py-openssl wget

RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
&& apk add jpeg-dev zlib-dev libjpeg \
&& pip install --upgrade pip


RUN pip install psutil

RUN cd /action; pip install -r requirements.txt

# Ensure source assets are not drawn from the cache 
# after this date
ENV REFRESHED_AT 2016-09-05T13:59:39Z
# Add all source assets
ADD . /action
# Rename our executable Python action
ADD performance.py /action/exec

# Leave CMD as is for Openwhisk
CMD ["/bin/bash", "-c", "cd actionProxy && python3 -u actionproxy.py"]