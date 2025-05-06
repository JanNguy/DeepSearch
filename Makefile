.PHONY: setup run

setup:
	python3.11 -m venv hackathon
	. hackathon/bin/activate && pip install -r requirement.txt

run:
	. hackathon/bin/activate && python main.py