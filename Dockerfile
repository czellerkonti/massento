FROM python:alpine

ADD src/pkg /opt/transcoder/
ENV MASSENTO_SCAN_DELAY=10
ENV MASSENTO_LOGLEVEL=INFO
CMD [ "python", "/opt/transcoder -d" ]
