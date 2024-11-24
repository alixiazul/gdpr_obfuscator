#################################################################################
#
# Makefile to build the project "GDPR Obfuscator"
#
#################################################################################

PROJECT_NAME = gdpr_obfuscator
REGION = eu-west-2
PYTHON_INTERPRETER = python
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash
PROFILE = default
PIP:=pip

## Create python interpreter environment
create-environment:
	@echo ">>> Setting up environment for $(PROJECT_NAME)..."
	( \
		$(PYTHON_INTERPRETER) -m venv venv; \
	) 

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install pip-tools)
	$(call execute_in_env, $(PIP) install --upgrade pip)


################################################################################################################
# Set Up
## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install safety
safety:
	$(call execute_in_env, $(PIP) install safety)

## Install black
black:
	$(call execute_in_env, $(PIP) install black)

## Install coverage
coverage:
	$(call execute_in_env, $(PIP) install coverage)

## Set up dev requirements (bandit, safety, black)
dev-setup: bandit safety black coverage

# Build / Run

## Run the security test (bandit + safety)
security-test:
	$(call execute_in_env, safety scan -r ./requirements.txt)
	$(call execute_in_env, bandit */*.py -n 3 -lll)

## Run the black code check
run-black:
	$(call execute_in_env, black gdpr_obfuscator test)

## Run the unit tests
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vvvrP --testdox test)

## Clean up .pyc files and any other temporary files
clean:
	$(call execute_in_env, find . -name "*.pyc" -exec rm -f {} \;)

## Run the report coverage  
report-coverage: coverage
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} coverage run -m pytest -vvvrP --testdox test)
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} coverage report -m)

## Upgrade libraies
upgrade-libraries:
	$(call execute_in_env, $(PIP) freeze | awk -F '==' '{print $$1}' | xargs $(PIP) install --upgrade)
