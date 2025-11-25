#!/bin/bash
# Quick script to check emails and process them

echo "Checking for emails..."
curl -X POST http://localhost:5000/api/check-emails \
  -H "Content-Type: application/json" \
  -d '{"auto_process": true, "mark_read": true}' \
  | python3 -m json.tool




