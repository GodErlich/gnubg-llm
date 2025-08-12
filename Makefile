# GNU Backgammon Setup Makefile

.PHONY: all install deps clone build test clean help
.DEFAULT_GOAL := help

# Configuration
GNUBG_WORKSPACE := $(HOME)/gnubg-workspace
GNUBG_DIR := $(GNUBG_WORKSPACE)/gnubg
GNUBG_REPO := https://git.savannah.gnu.org/git/gnubg.git
GNUBG_BRANCH := release-1_08_003
JOBS := $(shell nproc)

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)🎯 GNU Backgammon Setup Makefile$(NC)"
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

all: deps clone build install-python test ## Complete setup (default target)
	@echo "$(GREEN)✅ GNU Backgammon installed successfully! 🎉$(NC)"

deps: ## Install system dependencies
	@echo "$(YELLOW)📦 Installing system dependencies...$(NC)"
	sudo apt-get update
	sudo apt-get install -y \
		python3 python3-pip python3-dev python3-venv git wget build-essential \
		automake autoconf libtool pkg-config libglib2.0-dev libreadline-dev \
		libxml2-dev libxslt1-dev flex bison texinfo swig
	@echo "$(GREEN)✅ System dependencies installed$(NC)"

$(GNUBG_WORKSPACE):
	@echo "$(YELLOW)📁 Creating workspace directory...$(NC)"
	mkdir -p $(GNUBG_WORKSPACE)

clone: $(GNUBG_WORKSPACE) ## Clone GNU Backgammon repository
	@echo "$(YELLOW)📥 Cloning GNU Backgammon repository...$(NC)"
	@if [ ! -d "$(GNUBG_DIR)" ]; then \
		cd $(GNUBG_WORKSPACE) && \
		git clone --depth 1 --branch $(GNUBG_BRANCH) $(GNUBG_REPO); \
		echo "$(GREEN)✅ Repository cloned$(NC)"; \
	else \
		echo "$(GREEN)✅ Repository already exists$(NC)"; \
	fi

configure: clone ## Configure GNU Backgammon build
	@echo "$(YELLOW)⚙️ Configuring GNU Backgammon...$(NC)"
	cd $(GNUBG_DIR) && \
	./autogen.sh && \
	./configure --without-gtk --enable-simd=sse2 --enable-python
	@echo "$(GREEN)✅ Configuration complete$(NC)"

build: configure ## Build GNU Backgammon
	@echo "$(YELLOW)🔨 Building GNU Backgammon (using $(JOBS) jobs)...$(NC)"
	cd $(GNUBG_DIR) && make -j$(JOBS)
	@echo "$(GREEN)✅ Build complete$(NC)"

install-gnubg: build ## Install GNU Backgammon system-wide
	@echo "$(YELLOW)📦 Installing GNU Backgammon...$(NC)"
	cd $(GNUBG_DIR) && sudo make install
	sudo ldconfig
	@echo "$(GREEN)✅ GNU Backgammon installed$(NC)"

install-python: ## Install Python dependencies
	@echo "$(YELLOW)🐍 Installing Python dependencies...$(NC)"
	@if [ -f "requirements.txt" ]; then \
		pip3 install --user -r requirements.txt; \
		echo "$(GREEN)✅ Python dependencies installed$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ No requirements.txt found, skipping Python dependencies$(NC)"; \
	fi

install: install-gnubg install-python ## Install both GNU Backgammon and Python dependencies

test: ## Test GNU Backgammon installation
	@echo "$(YELLOW)🧪 Testing GNU Backgammon installation...$(NC)"
	@if gnubg --version > /dev/null 2>&1; then \
		echo "$(GREEN)✅ GNU Backgammon test passed$(NC)"; \
	else \
		echo "$(RED)❌ GNU Backgammon installation failed!$(NC)"; \
		exit 1; \
	fi

clean: ## Clean build artifacts
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	@if [ -d "$(GNUBG_DIR)" ]; then \
		cd $(GNUBG_DIR) && make clean > /dev/null 2>&1 || true; \
		echo "$(GREEN)✅ Build artifacts cleaned$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ No build directory found$(NC)"; \
	fi

clean-all: ## Remove entire workspace (WARNING: destructive)
	@echo "$(RED)🗑️ Removing entire workspace...$(NC)"
	@read -p "Are you sure you want to remove $(GNUBG_WORKSPACE)? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf $(GNUBG_WORKSPACE); \
		echo "$(GREEN)✅ Workspace removed$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled$(NC)"; \
	fi

uninstall: ## Uninstall GNU Backgammon from system
	@echo "$(YELLOW)🗑️ Uninstalling GNU Backgammon...$(NC)"
	@if [ -d "$(GNUBG_DIR)" ]; then \
		cd $(GNUBG_DIR) && sudo make uninstall; \
		sudo ldconfig; \
		echo "$(GREEN)✅ GNU Backgammon uninstalled$(NC)"; \
	else \
		echo "$(RED)❌ Build directory not found, cannot uninstall$(NC)"; \
		exit 1; \
	fi

update: ## Update GNU Backgammon to latest version
	@echo "$(YELLOW)🔄 Updating GNU Backgammon...$(NC)"
	@if [ -d "$(GNUBG_DIR)" ]; then \
		cd $(GNUBG_DIR) && \
		git fetch origin $(GNUBG_BRANCH) && \
		git reset --hard origin/$(GNUBG_BRANCH) && \
		$(MAKE) build install; \
		echo "$(GREEN)✅ GNU Backgammon updated$(NC)"; \
	else \
		echo "$(RED)❌ Repository not found, run 'make clone' first$(NC)"; \
		exit 1; \
	fi

status: ## Show installation status
	@echo "$(YELLOW)📊 Installation Status:$(NC)"
	@echo -n "System dependencies: "
	@if command -v autoconf > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "Workspace directory: "
	@if [ -d "$(GNUBG_WORKSPACE)" ]; then echo "$(GREEN)✅ Exists$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "GNU Backgammon source: "
	@if [ -d "$(GNUBG_DIR)" ]; then echo "$(GREEN)✅ Cloned$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "GNU Backgammon binary: "
	@if command -v gnubg > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "Python dependencies: "
	@if pip3 show requests > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi

# Error handling for common issues
check-sudo: ## Check if sudo is available
	@if ! command -v sudo > /dev/null 2>&1; then \
		echo "$(RED)❌ sudo is required but not available$(NC)"; \
		exit 1; \
	fi

check-git: ## Check if git is available
	@if ! command -v git > /dev/null 2>&1; then \
		echo "$(RED)❌ git is required but not available$(NC)"; \
		echo "$(YELLOW)Run: sudo apt-get install git$(NC)"; \
		exit 1; \
	fi

# Development targets
dev-setup: deps clone configure ## Setup for development (no install)
	@echo "$(GREEN)✅ Development environment ready$(NC)"

quick-build: ## Quick rebuild without reconfiguration
	@echo "$(YELLOW)🔨 Quick rebuilding GNU Backgammon...$(NC)"
	@if [ -d "$(GNUBG_DIR)" ]; then \
		cd $(GNUBG_DIR) && make -j$(JOBS); \
		echo "$(GREEN)✅ Quick build complete$(NC)"; \
	else \
		echo "$(RED)❌ Build directory not found, run 'make configure' first$(NC)"; \
		exit 1; \
	fi