FROM node:8-stretch

ENV HOST="127.0.0.1"
ENV PORT="28101"
ENV MJML_ARGS="--mjml.minify=true --mjml.validationLevel=strict"

ENV MJML_VERSION=4.0.5
ENV APP_DIR=/app

WORKDIR $APP_DIR

RUN npm install mjml@${MJML_VERSION}

COPY mjml/node/tcpserver.js $APP_DIR/

ENTRYPOINT ["/bin/sh", "-c", "node tcpserver.js $MJML_ARGS --host=$HOST --port=$PORT"]
