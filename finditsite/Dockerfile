FROM python:3.9-alpine
LABEL maintainer="londonappdeveloper.com"

ENV PYTHONUNBUFFERED 1

COPY ./finditsite/requirements.txt /tmp/requirements.txt
COPY ./finditsite/requirements.dev.txt /tmp/requirements.dev.txt
COPY ./finditsite /finditsite
WORKDIR /finditsite
EXPOSE 8000

ARG DEV=false

RUN apk add --update --no-cache \
    build-base \
    postgresql-client \
    postgresql-dev \
    musl-dev \
    tcl-dev \
    tk-dev \
    tcl \
    tk \
    ninja \
    libffi-dev \
    gcc \
    g++ \
    libxml2-dev \
    zlib-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*


RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    apk add --update --no-cache tcl-dev tk-dev && \
    apk add --update --no-cache tcl tk && \
    apk add --no-cache ninja && \
    /py/bin/pip install opencv-python-headless && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user
