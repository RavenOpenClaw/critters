.PHONY: setup test clean

setup:
	@echo "Setting up virtual environment and dependencies..."
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install pygame pytest hypothesis

test:
	@echo "Running tests..."
	PYTHONPATH=src venv/bin/python -m pytest tst/ -v

breed:
	@echo "Running breeding simulation..."
	PYTHONPATH=src venv/bin/python tst/simulate_breeding.py

play:
	@echo "Lauching Critters..."
	python3 src/main.py

clean:
	@echo "Cleaning up virtual environment and caches..."
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .hypothesis