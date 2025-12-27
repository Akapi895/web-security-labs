#!/bin/bash
# Wait for MSSQL to start
sleep 30

# Run the init script
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -i /docker-entrypoint-initdb.d/init.sql
