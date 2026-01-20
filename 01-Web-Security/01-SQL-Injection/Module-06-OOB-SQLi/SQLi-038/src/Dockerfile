FROM python:3.11-slim

# Install Oracle Instant Client
RUN apt-get update && apt-get install -y \
    libaio1t64 wget unzip \
    && wget https://download.oracle.com/otn_software/linux/instantclient/2114000/instantclient-basic-linux.x64-21.14.0.0.0dbru.zip \
    && unzip instantclient-basic-linux.x64-21.14.0.0.0dbru.zip -d /opt/oracle \
    && rm instantclient-basic-linux.x64-21.14.0.0.0dbru.zip \
    && echo /opt/oracle/instantclient_21_14 > /etc/ld.so.conf.d/oracle.conf \
    && ldconfig \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_14:$LD_LIBRARY_PATH

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
