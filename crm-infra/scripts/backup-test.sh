#!/bin/bash

# Directory containing backups
BACKUP_DIR="backups"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory $BACKUP_DIR does not exist."
  exit 1
fi

# List available backups with details
echo "Available backups:"
ls -lh "$BACKUP_DIR"
