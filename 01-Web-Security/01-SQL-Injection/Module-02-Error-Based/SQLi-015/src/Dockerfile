FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libaio1t64 wget unzip && rm -rf /var/lib/apt/lists/*
RUN wget -q https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && unzip -q instantclient-basiclite-linuxx64.zip -d /opt/oracle && rm instantclient-basiclite-linuxx64.zip && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle.conf && ldconfig
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_1:$LD_LIBRARY_PATH
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
