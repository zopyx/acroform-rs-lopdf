.PHONY: help sdist build publish test test-rust test-python clean lint format develop

PYTHON := python3
VENV := .venv
MATURIN := $(VENV)/bin/maturin
UV := uv

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

develop: ## Build and install the package in development mode
	$(UV) pip install maturin
	$(MATURIN) develop --release

build: ## Build Python wheels for all platforms
	$(MATURIN) build --release

sdist: ## Create a source distribution
	$(MATURIN) sdist

publish: ## Publish to PyPI (requires MATURIN_PYPI_TOKEN env var)
	$(MATURIN) publish

test: test-rust test-python ## Run all tests

test-rust: ## Run Rust tests
	cargo test

test-python: ## Run Python tests
	$(UV) run pytest python/tests/ -v

lint: ## Run linters on Python code
	$(UV) run ruff check python/
	$(UV) run ty check python/

format: ## Format Python and Rust code
	$(UV) run ruff format python/
	cargo fmt

clean: ## Clean build artifacts
	rm -rf target/
	rm -rf dist/
	rm -rf python/acroform/*.so
	rm -rf python/acroform/__pycache__
	rm -rf python/tests/__pycache__
	rm -rf .pytest_cache
	cargo clean

venv: ## Create a virtual environment
	$(UV) venv $(VENV) --python 3.12
	$(UV) pip install maturin pytest ruff ty

install-dev: venv develop ## Setup development environment
