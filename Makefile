.PHONY: help sdist build build-all build-macos build-linux build-cross \
	publish test test-rust test-python clean lint format develop venv install-dev \
	release-local release-check

PYTHON := python3
VENV := .venv
MATURIN := $(VENV)/bin/maturin
UV := uv

# Python versions for wheel builds
PYTHON_VERSIONS := python3.12 python3.13

# Maturin interpreter flags for multiple Python versions
MATURIN_INTERPRETERS := $(foreach py,$(PYTHON_VERSIONS),-i $(py))

# Detect Rust toolchain type (rustup vs homebrew)
# Rustup uses ~/.rustup, Homebrew uses /opt/homebrew/Cellar/rust
RUST_TOOLCHAIN := $(shell rustc --print sysroot 2>/dev/null | grep -q ".rustup" && echo "rustup" || echo "system")

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

develop: ## Build and install the package in development mode
	$(UV) pip install maturin
	$(MATURIN) develop --release

build: ## Build Python wheel for current platform (default Python version)
	$(MATURIN) build --release

build-all: ## Build Python wheels for Python 3.12 and 3.13 (current platform)
	$(MATURIN) build --release $(MATURIN_INTERPRETERS)
	@echo ""
	@echo "=== Build complete ==="
	@echo "Wheels are in: target/wheels/"
	@ls -lh target/wheels/*.whl 2>/dev/null || true

build-macos: ## Build macOS wheels for Python 3.12 and 3.13 (current arch only with Homebrew Rust)
	$(MATURIN) build --release $(MATURIN_INTERPRETERS)
	@echo ""
	@echo "=== Build complete ==="
	@echo "Wheels are in: target/wheels/"
	@ls -lh target/wheels/*.whl 2>/dev/null || true

build-linux: ## Build Linux wheels using zig cross-compilation (requires rustup)
ifneq ($(RUST_TOOLCHAIN),rustup)
	$(error "Cross-compilation requires rustup. Install from https://rustup.rs/ or use CI/CD")
endif
	$(MATURIN) build --release --zig --target aarch64-unknown-linux-gnu $(MATURIN_INTERPRETERS)
	$(MATURIN) build --release --zig --target x86_64-unknown-linux-gnu $(MATURIN_INTERPRETERS)

build-cross: build-macos ## Build wheels for macOS (adds Linux if rustup available)
ifeq ($(RUST_TOOLCHAIN),rustup)
	$(MAKE) build-linux
endif
	@echo ""
	@echo "=== Build complete ==="
	@echo "Wheels are in: target/wheels/"
	@ls -lh target/wheels/*.whl 2>/dev/null || true
	@echo ""
ifeq ($(RUST_TOOLCHAIN),system)
	@echo "Note: Linux wheels not built (requires rustup)"
	@echo "Install rustup: curl --proto '=https' --tlsv1.2 -sSf https://rustup.rs | sh"
endif

build-universal2: ## Build universal2 macOS wheels (ARM64 + x86_64, requires rustup)
ifneq ($(RUST_TOOLCHAIN),rustup)
	$(error "Universal2 builds require rustup. Install from https://rustup.rs/")
endif
	rustup target add x86_64-apple-darwin aarch64-apple-darwin
	$(MATURIN) build --release --target universal2-apple-darwin $(MATURIN_INTERPRETERS)

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

# Release helpers
release-check: ## Check release readiness (tests, format, etc.)
	@echo "=== Running release checks ==="
	@echo ""
	@echo "1. Running Rust tests..."
	cargo test --locked
	@echo ""
	@echo "2. Running Rust format check..."
	cargo fmt -- --check
	@echo ""
	@echo "3. Building wheels for current platform..."
	$(MAKE) build-all
	@echo ""
	@echo "=== Release checks passed ==="
	@echo ""
	@echo "To build and release for all platforms:"
	@echo "  1. Tag the release: git tag v0.2.1"
	@echo "  2. Push the tag: git push origin v0.2.1"
	@echo "  3. GitHub Actions will build and publish wheels for:"
	@echo "     - macOS ARM64 (Python 3.12, 3.13)"
	@echo "     - macOS x86_64 (Python 3.12, 3.13)"
	@echo "     - Linux ARM64 (Python 3.12, 3.13)"
	@echo "     - Linux x86_64 (Python 3.12, 3.13)"
	@echo "     - Source distribution"

release-local: clean build-all sdist ## Build release artifacts locally (current platform only)
	@echo "=== Release artifacts built ==="
	@ls -lh target/wheels/
	@echo ""
	@echo "To upload to PyPI:"
	@echo "  make publish"
	@echo ""
	@echo "Or upload manually:"
	@echo "  maturin upload target/wheels/*"

# CI/CD targets for building wheels on multiple platforms
build-wheels-macos: ## Build wheels for macOS (CI use)
	$(MATURIN) build --release $(MATURIN_INTERPRETERS)

build-wheels-linux: ## Build wheels for Linux (CI use, requires Linux runner)
	$(MATURIN) build --release $(MATURIN_INTERPRETERS)
