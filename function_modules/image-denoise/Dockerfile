# Dockerfile for Python whisk docker action
FROM openwhisk/dockerskeleton

ENV FLASK_PROXY_PORT 8080

## Install our action's Python dependencies
ADD requirements.txt /action/requirements.txt
ENV AWS_ACCESS_KEY_ID="AKIAYFB773UVZSOAVZN4"
ENV AWS_SECRET_ACCESS_KEY="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"
ENV AWS_REGION="ap-south-1"
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
&& apk add jpeg-dev zlib-dev libjpeg \
&& pip install --upgrade pip
RUN cd /action; pip install --no-cache-dir -r requirements.txt
RUN pip install opencv-python
# Ensure source assets are not drawn from the cache after this date
ENV REFRESHED_AT 2016-09-05T13:59:39Z
# Add all source assets
ADD . /action
# Rename our executable Python action
ADD denoise.py /action/exec

# Leave CMD as is for Openwhisk
CMD ["/bin/bash", "-c", "cd actionProxy && python3 -u actionproxy.py"]