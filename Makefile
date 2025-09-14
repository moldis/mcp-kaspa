.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	python -m pytest tests/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf kaspa_mcp_data/

lint:
	python -m flake8 . --max-line-length=120

format:
	python -m black .