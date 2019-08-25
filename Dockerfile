FROM python:alpine

RUN apk update
RUN apk add ffmpeg
ADD src/pkg /opt/massento/
ADD config.json /etc/massento/config.json
ADD start.sh /opt/start.sh
RUN mkdir /input
RUN mkdir /output
ENV MASSENTO_SCAN_DELAY=10
ENV MASSENTO_LOGLEVEL=INFO
#CMD [ "python", "/opt/massento", "-d", "-i /input/", "-r /output/" ]
CMD [ "/opt/start.sh" ]
