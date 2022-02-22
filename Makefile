.DEFAULT_GOAL := help

winbin:      ## Generate windows binary (.exe)
	pyinstaller --onefile -w main.py

install-dep: ## Install dependencies
	pip install -r requirements.txt

.PHONY: start
start:       ## Start game
start: install-dep
	python main.py

.PHONY: help
help:        ## Show this help text
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
