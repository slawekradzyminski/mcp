#!/bin/bash

PORT=7000
echo "Stopping MCP server on port $PORT..."
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
    
    if ps -p $SERVER_PID > /dev/null; then
      echo "ERROR: Failed to kill server process"
      exit 1
    else
      echo "Server terminated successfully with force kill"
    fi
  else
    echo "Server terminated successfully"
  fi
  
  exit 0
else
  echo "No server found running on port $PORT"
  exit 0
fi 