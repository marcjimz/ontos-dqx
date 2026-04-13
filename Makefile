.PHONY: help setup install deploy-dev deploy-qa deploy-prod sync-contracts-dev sync-contracts-qa sync-contracts-prod dqx-dev dqx-qa dqx-prod promote-qa promote-prod clean

ifneq (,$(wildcard .env))
    include .env
    export
endif

help: ## Show this help
	@echo "ontos-dqx: ODCS-Driven Data Quality with Ontos (Scripius PBM Demo)"
	@echo ""
	@echo "=== Setup ==="
	@echo "  make setup              Create .env from template"
	@echo "  make install            Install Python dependencies"
	@echo ""
	@echo "=== Deploy ==="
	@echo "  make deploy-dev         Deploy DDL + seed data to DEV"
	@echo "  make deploy-qa          Deploy DDL (no seed) to QA"
	@echo "  make deploy-prod        Deploy DDL (no seed) to PROD"
	@echo ""
	@echo "=== Contracts ==="
	@echo "  make sync-contracts-dev   Upload ODCS contracts to Ontos (DEV)"
	@echo "  make sync-contracts-qa    Upload ODCS contracts to Ontos (QA)"
	@echo "  make sync-contracts-prod  Upload ODCS contracts to Ontos (PROD)"
	@echo ""
	@echo "=== Quality Gate ==="
	@echo "  make dqx-dev            Run DQX quality checks against DEV"
	@echo "  make dqx-qa             Run DQX quality checks against QA"
	@echo "  make dqx-prod           Run DQX quality checks against PROD"
	@echo ""
	@echo "=== Promote ==="
	@echo "  make promote-qa         DEV -> QA (deploy + contracts + DQX gate)"
	@echo "  make promote-prod       QA -> PROD (deploy + contracts + DQX gate)"

setup: ## Create .env from template
	@if [ ! -f .env ]; then cp config/.env.example .env && echo "Created .env -- edit with your values"; else echo ".env already exists"; fi

install: ## Install Python dependencies
	pip install -r requirements.txt

deploy-dev: ## Deploy DDL + seed data to DEV
	python scripts/deploy.py --env dev --seed

deploy-qa: ## Deploy DDL (no seed) to QA
	python scripts/deploy.py --env qa

deploy-prod: ## Deploy DDL (no seed) to PROD
	python scripts/deploy.py --env prod

sync-contracts-dev: ## Sync ODCS contracts to Ontos (DEV)
	python scripts/sync_contracts.py --env dev

sync-contracts-qa: ## Sync ODCS contracts to Ontos (QA)
	python scripts/sync_contracts.py --env qa

sync-contracts-prod: ## Sync ODCS contracts to Ontos (PROD)
	python scripts/sync_contracts.py --env prod

dqx-dev: ## Run DQX quality gate against DEV
	python scripts/run_dqx.py --env dev

dqx-qa: ## Run DQX quality gate against QA
	python scripts/run_dqx.py --env qa

dqx-prod: ## Run DQX quality gate against PROD
	python scripts/run_dqx.py --env prod

promote-qa: ## Promote DEV -> QA
	python scripts/promote.py --source dev

promote-prod: ## Promote QA -> PROD
	python scripts/promote.py --source qa

clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
