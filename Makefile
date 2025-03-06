PROJECT_NAME = a3grpc

init:
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt

coverage:
	coverage erase
	coverage run --source=$(PROJECT_NAME) -m unittest discover
	coverage html
	python3 -m webbrowser ./htmlcov/index.html

test:
	tox -p

build:
	python -m build

clean:
	rm -rf build dist .egg *.egg-info

upload:
	twine upload dist/* --verbose

format:
	ruff format

check:
	ruff check
	mypy
