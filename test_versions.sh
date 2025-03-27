#!/bin/bash
# Test the version history functionality

echo "Running version history test..."
python manage.py shell < core/test_version_history.py

echo "Done!"