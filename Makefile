.PHONY: setup run

setup:
	python3.11 -m venv hackathon
	source hackathon/bin/activate && pip install -r requirement.txt

run:
	source hackathon/bin/activate && python app.py
