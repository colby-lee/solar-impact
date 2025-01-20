# Define the virtual environment and common paths
export PYTHONPATH := $(CURDIR)
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Ensure the virtual environment exists
$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

# Install dependencies
install: $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Run the data collector
run-data-collector: $(VENV_DIR)
	$(PYTHON) -m data_collector.collect

# Run the FastAPI server
run-server: $(VENV_DIR)
	$(PYTHON) -m uvicorn api.main:app --reload
