FROM node:14-bullseye

ARG MJML_VERSION=4.11.0
ARG TCPSERVER_VERSION=0.11.0
ARG APP_DIR=/app

RUN npm install mjml@${MJML_VERSION}

WORKDIR $APP_DIR

RUN curl -L https://raw.githubusercontent.com/liminspace/django-mjml/$TCPSERVER_VERSION/mjml/node/tcpserver.js \
    -o tcpserver.js

ENV HOST="0.0.0.0"
ENV PORT="28101"
ENV MJML_ARGS="--mjml.minify=true --mjml.validationLevel=strict"

EXPOSE 28101

CMD ["/bin/sh", "-c", "exec node tcpserver.js $MJML_ARGS --host=$HOST --port=$PORT"]
