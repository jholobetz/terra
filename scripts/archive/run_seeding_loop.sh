#!/bin/bash
# Infinite loop to run formula seeding and database sync.
# This ensures that even if individual requests hit transient 503 overloads,
# the process will make progress across all shards.

echo "🚀 Starting continuous GQS Formula Seeding Loop..."
cd "$(dirname "$0")/../.."

while true; do
  echo "================================================================================"
  echo "🪐 [$(date)] Commencing seeding pass..."
  echo "================================================================================"
  
  # Run the seed command using the free tier limits (cooldown)
  .venv/bin/python3 gqs.py seed free
  
  echo "================================================================================"
  echo "🔄 [$(date)] Commencing database sync..."
  echo "================================================================================"
  
  # Sync the database tables with the updated shards
  php cli_sync.php
  
  echo "================================================================================"
  echo "💤 [$(date)] Pass complete. Sleeping for 30 seconds..."
  echo "================================================================================"
  sleep 30
done
