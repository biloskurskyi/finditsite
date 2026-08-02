FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

ARG DEV=false

COPY ./finditsite/requirements.txt /tmp/requirements.txt
COPY ./finditsite/requirements.dev.txt /tmp/requirements.dev.txt
COPY ./finditsite /finditsite

WORKDIR /finditsite
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp/requirements.txt /tmp/requirements.dev.txt && \
    adduser --disabled-password --no-create-home django-user

ENV PATH="/py/bin:$PATH"

USER django-user
