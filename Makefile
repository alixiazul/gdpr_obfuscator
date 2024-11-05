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
