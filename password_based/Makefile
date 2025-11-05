# Makefile for Flask File Encryption Tool

.PHONY: help install run run-chrome clean setup venv

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup     - Create virtual environment and install dependencies"
	@echo "  make install   - Install Python dependencies"
	@echo "  make run       - Run the Flask application"
	@echo "  make run-chrome - Run Flask and open in Chrome automatically"
	@echo "  make clean     - Clean up temporary files"
	@echo "  make venv      - Create virtual environment only"

# Detect OS
UNAME_S := $(shell uname -s)

# Platform-specific commands
ifeq ($(UNAME_S),Linux)
	PYTHON = venv/bin/python
	PIP = venv/bin/pip
	CHROME_CMD = google-chrome || chromium-browser
	OPEN_CMD = xdg-open
endif
ifeq ($(UNAME_S),Darwin)
	PYTHON = venv/bin/python
	PIP = venv/bin/pip
	CHROME_CMD = open -a "Google Chrome"
	OPEN_CMD = open
endif
ifeq ($(OS),Windows_NT)
	PYTHON = venv\Scripts\python
	PIP = venv\Scripts\pip
	CHROME_CMD = start chrome
	OPEN_CMD = start
endif

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  On Windows: venv\Scripts\activate"
	@echo "  On macOS/Linux: source venv/bin/activate"

# Install dependencies
install: venv
	@echo "Installing dependencies..."
	$(PIP) install -q flask cryptography
	@echo "Dependencies installed successfully!"

# Setup project (first time)
setup: install
	@echo "Project setup complete!"
	@echo "Run 'make run' to start the application"

# Run the Flask application
run:
	pip install -r requirements.txt
	@echo "Starting Flask application..."
	$(PYTHON) app.py

# Run and open in Chrome
run-chrome:
	@echo "Starting Flask application and opening in Chrome..."
	@(sleep 3 && $(CHROME_CMD) "http://localhost:5000" 2>/dev/null || $(OPEN_CMD) "http://localhost:5000" 2>/dev/null || echo "Please open http://localhost:5000 manually") &
	$(PYTHON) app.py

# Run in development mode with auto-reload
dev:
	@echo "Starting Flask in development mode..."
	FLASK_APP=app.py FLASK_ENV=development $(PYTHON) -m flask run

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf uploads/*
	rm -f *.pyc
	@echo "Cleanup complete!"

# Install production dependencies
prod-install:
	pip install -r requirements.txt

# Create requirements file
requirements:
	$(PIP) freeze > requirements.txt

# Show project info
info:
	@echo "Flask File Encryption Tool"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo 'Not in venv')"
	@echo "Virtual Environment: $(shell which $(PYTHON) >/dev/null 2>&1 && echo 'Active' || echo 'Not active')"
	@echo "Available routes:"
	@echo "  http://localhost:5000/ - Main interface"
	@echo "  http://localhost:5000/encrypt - Encryption endpoint"
	@echo "  http://localhost:5000/decrypt - Decryption endpoint"

