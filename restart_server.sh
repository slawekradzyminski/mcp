#!/bin/bash

PORT=7000
MAX_RETRIES=10
RETRY_INTERVAL=2

echo "Stopping any running MCP server on port $PORT..."
SERVER_PID=$(lsof -t -i:$PORT 2>/dev/null)

if [ -n "$SERVER_PID" ]; then
  echo "Found server process: $SERVER_PID - terminating..."
  kill $SERVER_PID
  # Give it a moment to terminate
  sleep 2

  # Check if it's still running and force kill if necessary
  if ps -p $SERVER_PID > /dev/null; then
    echo "Server process didn't terminate gracefully, force killing..."
    kill -9 $SERVER_PID
    sleep 1
  fi
else
  echo "No server found running on port $PORT"
fi

echo "Starting MCP server..."
source venv/bin/activate
python -m mcp_simple_tool > server.log 2>&1 &
SERVER_PID=$!

# Check if process started successfully
if ! ps -p $SERVER_PID > /dev/null; then
  echo "Failed to start server process"
  exit 1
fi

echo "Server process started with PID: $SERVER_PID"

# Wait for server to become responsive
echo "Waiting for server to become responsive..."
for ((i=1; i<=MAX_RETRIES; i++)); do
  echo "Attempt $i of $MAX_RETRIES..."
  
  # Use HEAD request with timeout to avoid hanging on SSE connection
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 1 --max-time 2 -X HEAD http://localhost:$PORT/sse 2>/dev/null)
  
  if [[ "$HTTP_STATUS" =~ ^(200|4[0-9][0-9])$ ]]; then
    # Accept 200 or any 4xx status as sign that server is running
    echo "Server is up and running!"
    echo "Server URL: http://localhost:$PORT/sse"
    exit 0
  fi
  
  # If we've reached max retries, check if process is still running
  if [ $i -eq $MAX_RETRIES ]; then
    if ps -p $SERVER_PID > /dev/null; then
      echo "Server process is running but not responding. Check server.log for errors."
    else
      echo "Server process has terminated unexpectedly. Check server.log for errors."
    fi
    exit 1
  fi
  
  sleep $RETRY_INTERVAL
done

echo "Server failed to start properly within the expected time"
exit 1 