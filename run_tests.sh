#!/bin/bash
# Script to run tests (excluding UI tests that require display)

echo "Running unit tests for validators..."
python -m pytest tests/unit/test_validators.py -v -p no:qt

echo ""
echo "Running unit tests for client..."
python -m pytest tests/unit/test_client.py -v -p no:qt

echo ""
echo "Running integration tests..."
python -m pytest tests/integration/test_api_integration.py -v -p no:qt

echo ""
echo "Running coverage report..."
python -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=term-missing --cov-report=html -p no:qt

echo ""
echo "Tests completed!"
