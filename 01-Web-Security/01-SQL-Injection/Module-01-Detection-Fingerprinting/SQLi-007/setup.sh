#!/bin/bash

# Wait for SQL Server to start
sleep 30s

# Run the init script
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -i /init.sql
