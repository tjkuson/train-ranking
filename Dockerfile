FROM fedora:37 as base

WORKDIR /app

# Install dependencies
RUN dnf install -y python3 python3-pip && \
    dnf clean all

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
