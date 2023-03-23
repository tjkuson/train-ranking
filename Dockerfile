FROM ubuntu:latest as base

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip cron

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
