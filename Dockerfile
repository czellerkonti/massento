FROM python:alpine

ADD src/pkg /opt/transcoder/

CMD [ "python", "/opt/transcoder" ]
