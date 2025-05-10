#!/bin/bash

PORT=7000

# Check if something is running on the port
SERVER_PID=$(lsof -t -i:$PORT 2>/dev/null)

if [ -n "$SERVER_PID" ]; then
  echo "Server process found with PID: $SERVER_PID"
  
  # Check if server is responsive - using HEAD request with timeout
  # Note: For SSE endpoints, we use a quick timeout since we don't want to wait for data
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 1 --max-time 2 -X HEAD http://localhost:$PORT/sse 2>/dev/null)
  
  if [[ "$HTTP_STATUS" =~ ^(200|4[0-9][0-9])$ ]]; then
    # Accept 200 or any 4xx status as sign that server is running
    echo "Server is up and running at http://localhost:$PORT/sse"
    exit 0
  else
    echo "Server process is running but not responding properly (Status: $HTTP_STATUS)"
    exit 1
  fi
else
  echo "No server process found running on port $PORT"
  exit 1
fi 