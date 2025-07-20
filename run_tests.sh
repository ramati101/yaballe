#!/bin/bash
echo "⏳ Waiting for Mongo and Redis..."
sleep 5
echo "🚀 Running tests..."
pytest tests/
