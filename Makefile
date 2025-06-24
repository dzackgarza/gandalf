# Makefile for the Gandalf Trust Framework

# Ensure that PROMPT is set, but allow it to be overridden from the command line
PROMPT ?= default_prompt

# Default target
.PHONY: default
default: develop

# Target to install dependencies using uv and the lockfile
.PHONY: install
install:
	@echo "--- Ensuring virtual environment exists and installing dependencies ---"
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment using uv..."; \
		uv venv; \
	fi
	uv pip sync requirements.txt --python .venv/bin/python
	@echo "✅ Virtual environment ready and dependencies installed."

# Target to compile requirements.in to requirements.txt (lock the dependencies)
.PHONY: lock
lock:
	@echo "--- Compiling requirements.in to requirements.txt using uv ---"
	uv pip compile requirements.in -o requirements.txt
	@echo "✅ Lockfile requirements.txt generated."

# Target for the main development workflow
.PHONY: develop
develop: install
	@echo "--- Starting development workflow for prompt: $(PROMPT) ---"
	@echo "--- [DEV] Performing placeholder code generation and scaffolding ---"
	mkdir -p gandalf_workshop/blueprints
	mkdir -p gandalf_workshop/artisan_guildhall/inspectors
	mkdir -p gandalf_workshop/specs
	touch gandalf_workshop/__init__.py # Ensure gandalf_workshop is a package
	touch "gandalf_workshop/$(PROMPT).py"
	echo "# Placeholder file for feature: $(PROMPT)" > "gandalf_workshop/$(PROMPT).py"
	touch main.py
	echo "# Main entry point" > main.py
	touch gandalf_workshop/specs/data_models.py
	echo "# Data models" > gandalf_workshop/specs/data_models.py
	cp auditing/scaffold_templates/workshop_manager.template.py gandalf_workshop/workshop_manager.py
	cp auditing/scaffold_templates/test_workshop_manager.template.py gandalf_workshop/tests/test_workshop_manager.py
	@echo "✅ Placeholder code and scaffold generated."

	@echo "--- [DEV] Running full audit pipeline ---"
	auditing/run_full_audit.sh

	@echo "--- [DEV] Audit successful, preparing commit ---"
	git add auditing/LATEST_AUDIT_RECEIPT.md gandalf_workshop/__init__.py "gandalf_workshop/$(PROMPT).py" main.py gandalf_workshop/workshop_manager.py gandalf_workshop/specs/data_models.py gandalf_workshop/blueprints/ gandalf_workshop/artisan_guildhall/inspectors/ gandalf_workshop/tests/
	git commit -m "feat: Implement $(PROMPT) and pass audit" -m "Generated auditing/LATEST_AUDIT_RECEIPT.md for commit. Basic scaffold created."
	@echo "✅ Feature $(PROMPT) and audit receipt committed."

# Target to run the full audit pipeline directly
.PHONY: audit
audit:
	@echo "--- Running full audit pipeline ---"
	auditing/run_full_audit.sh
	@echo "✅ Audit pipeline finished."

# Target to clean up generated files
.PHONY: clean
clean:
	@echo "--- Cleaning up generated files ---"
	rm -f gandalf_workshop/*.py
	rm -f auditing/LATEST_AUDIT_RECEIPT.md
	rm -rf gandalf_workshop/__pycache__
	rm -rf gandalf_workshop/tests/__pycache__
	rm -f gandalf_workshop/tests/test_dummy.py
	rm -f .coverage
	@echo "✅ Cleanup complete."
