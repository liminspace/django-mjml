FROM node:8-stretch

ARG MJML_VERSION=4.3.1
ARG APP_DIR=/app

RUN npm install mjml@${MJML_VERSION}

WORKDIR $APP_DIR

COPY mjml/node/tcpserver.js $APP_DIR/

ENV HOST="0.0.0.0"
ENV PORT="28101"
ENV MJML_ARGS="--mjml.minify=true --mjml.validationLevel=strict"

EXPOSE 28101

ENTRYPOINT ["/bin/sh", "-c", "exec node tcpserver.js $MJML_ARGS --host=$HOST --port=$PORT"]
