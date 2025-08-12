# GNU Backgammon Setup Makefile

.PHONY: all install deps clone build test clean help
.DEFAULT_GOAL := help


# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)🎯 GNU Backgammon Setup Makefile$(NC)"
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

all: install-gnubg install-python test ## Complete setup (default target)
	@echo "$(GREEN)✅ GNU Backgammon installed successfully! 🎉$(NC)"

deps: ## Install system dependencies
	@echo "$(YELLOW)📦 Installing system dependencies...$(NC)"
	sudo apt-get update
	sudo apt-get install -y python3 python3-pip python3-dev python3-venv git wget
	@echo "$(GREEN)✅ System dependencies installed$(NC)"


install-gnubg: ## Install GNU Backgammon via apt
	@echo "$(YELLOW)📦 Installing GNU Backgammon via apt...$(NC)"
	sudo apt update
	sudo apt install -y gnubg
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

clean: ## Clean apt cache
	@echo "$(YELLOW)🧹 Cleaning apt cache...$(NC)"
	sudo apt autoremove -y
	sudo apt autoclean
	@echo "$(GREEN)✅ Apt cache cleaned$(NC)"

uninstall: ## Uninstall GNU Backgammon from system
	@echo "$(YELLOW)🗑️ Uninstalling GNU Backgammon...$(NC)"
	sudo apt remove -y gnubg
	sudo apt autoremove -y
	@echo "$(GREEN)✅ GNU Backgammon uninstalled$(NC)"

update: ## Update GNU Backgammon to latest version
	@echo "$(YELLOW)🔄 Updating GNU Backgammon...$(NC)"
	sudo apt update
	sudo apt upgrade -y gnubg
	@echo "$(GREEN)✅ GNU Backgammon updated$(NC)"

status: ## Show installation status
	@echo "$(YELLOW)📊 Installation Status:$(NC)"
	@echo -n "GNU Backgammon binary: "
	@if command -v gnubg > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "Python dependencies: "
	@if pip3 show requests > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi
	@echo -n "System dependencies: "
	@if command -v python3 > /dev/null 2>&1; then echo "$(GREEN)✅ Installed$(NC)"; else echo "$(RED)❌ Missing$(NC)"; fi

# Error handling for common issues
check-sudo: ## Check if sudo is available
	@if ! command -v sudo > /dev/null 2>&1; then \
		echo "$(RED)❌ sudo is required but not available$(NC)"; \
		exit 1; \
	fi

