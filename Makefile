.SILENT:
.DEFAULT_GOAL: help

help:
	echo "USAGE"
	echo "  make <commands>"
	echo ""
	echo "AVAILABLE COMMANDS"
	echo "  run		Start the bot"
	echo "  install	Install dependencies"
	echo "  flake		Run flake8"
	echo "  isort		Run isort"

install:
	pip install -r requirements.txt

run:
	python3 main.py

isort:
	python3 isort .

flake:
	python3 flake8