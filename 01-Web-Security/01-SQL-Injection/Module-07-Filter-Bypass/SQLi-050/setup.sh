#!/bin/bash
sleep 30
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -C -i /docker-entrypoint-initdb.d/init.sql
