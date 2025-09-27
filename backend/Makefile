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
	echo "PYTHONPATH: $(PYTHONPATH)"  
	$(PYTHON) -m uvicorn api.main:app --reload

# Run unit tests
run-tests: 
	$(VENV_DIR)/bin/pytest -v

# Run api tests
run-api-tests:
	(VENV_DIR)/bin/pytest api/tests -v


################################# Heroku setup ########################################
APP_NAME = solar-impact-api
REPO_ROOT = $(abspath $(dir $(MAKEFILE_LIST))..)

# Deploy
deploy-heroku:
	cd $(REPO_ROOT) && git subtree push --prefix backend heroku master

# Start Heroku App
start-heroku:
	heroku ps:scale web=1 -a $(APP_NAME) || true
	heroku ps:scale worker=1 -a solar-impact-api
	heroku addons:create heroku-postgresql:essential-0 -a $(APP_NAME) --wait || true
	heroku addons:create cloudamqp:lemur -a $(APP_NAME) --wait || true
	make push-env

# Stop Heroku App
stop-heroku:
	heroku ps:scale web=0 -a $(APP_NAME) || true
	heroku ps:scale worker=0 -a solar-impact-api
	heroku addons:destroy heroku-postgresql -a $(APP_NAME) --confirm $(APP_NAME) || true
	heroku addons:destroy cloudamqp -a $(APP_NAME) --confirm $(APP_NAME) || true

heroku-down:
	heroku ps:scale web=0 worker=0 -a solar-impact-api

heroku-up:
	heroku	ps:scale web=1 worker=1 -a solar-impact-api


# Push local .env to Heroku 
push-env:
	@if [ -f ./.env ]; then \
		export $$(cat ../.env | xargs) && \
		heroku config:set \
		NASA_API_KEY=$$NASA_API_KEY \
		-a $(APP_NAME); \
	else \
		echo ".env file not found in project root"; \
	fi

# Show current config
show-config:
	heroku config -a $(APP_NAME)

