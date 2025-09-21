# Run tests script
# run_tests.sh
"""
#!/bin/bash

echo "Running Django Tests with Coverage..."

# Install test dependencies
pip install pytest pytest-django pytest-cov factory-boy

# Run tests with coverage
python -m pytest --cov=. --cov-report=html --cov-report=term --cov-fail-under=80

# Generate coverage report
echo "Coverage report generated in htmlcov/index.html"

# Run specific test categories
echo "Running unit tests..."
python -m pytest -v -k "test_" --cov=. --cov-report=term

echo "Running integration tests..."
python -m pytest -v -k "TestAPI" --cov=. --cov-report=term

# Check for any missing tests
echo "Checking test coverage..."
coverage report --show-missing
"""


# Makefile for test commands
"""
# Makefile

.PHONY: test test-unit test-integration test-coverage test-fast

test:
	python -m pytest --cov=. --cov-report=html --cov-report=term

test-unit:
	python -m pytest -v tests/ -k "not integration"

test-integration:
	python -m pytest -v tests/ -k "integration"

test-coverage:
	python -m pytest --cov=. --cov-report=html --cov-report=term --cov-fail-under=85

test-fast:
	python -m pytest -x --ff

lint:
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

install-dev:
	pip install -r requirements-dev.txt

setup-test-db:
	python manage.py migrate --settings=ecommerce_api.test_settings
	python manage.py loaddata fixtures/test_data.json --settings=ecommerce_api.test_settings
"""