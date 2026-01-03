#!/bin/bash
sleep 30s
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -i /init.sql
