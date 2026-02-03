#!/bin/bash

# Simple healthcheck script for the API service
# Usage: ./healthcheck.sh [URL]

URL=${1:-"http://localhost/api/health"}

# Perform HTTP request and capture status code
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

# Check status code and report
if [ "$STATUS" = "200" ]; then
  echo "Health check OK: $STATUS"
  exit 0
else
  echo "Health check failed: $STATUS"
  exit 1
fi
