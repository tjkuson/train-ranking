FROM fedora:37 as base

WORKDIR /app

# Install dependencies
RUN dnf install -y wget java-11-openjdk python3 python3-pip && \
    dnf clean all

# Install Apache Spark
RUN wget https://downloads.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz && \
    tar -xvzf spark-3.3.2-bin-hadoop3.tgz && \
    mv spark-3.3.2-bin-hadoop3 /opt/spark && \
    rm spark-3.3.2-bin-hadoop3.tgz

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
