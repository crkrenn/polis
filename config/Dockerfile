FROM node:14.5.0-alpine

ENV POLIS_ROOT=/
WORKDIR ${POLIS_ROOT}config

COPY config/package*.json ./
RUN npm install

COPY config/ ./

RUN node export_config.js

RUN echo done
