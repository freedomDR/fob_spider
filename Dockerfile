FROM python:3.6-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apk -U add \
        libxml2-dev\
        libxslt-dev\
        openssl-dev\
        libffi-dev
RUN apk --update  add --virtual .build-deps\
        musl-dev\
        gcc
RUN pip install -r requirements.txt
RUN apk del .build-deps
COPY . .
CMD ["scrapy", "crawl", "bbs"]
