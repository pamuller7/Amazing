run: venv
	./venv/bin/python3 -m poetry run python3.10 a_maze_ing.py config.txt

test: venv
	./venv/bin/python3 -m poetry run python3.10 -m unittest tests/parsing.py tests/validity.py

venv: install

install: .installed

.installed:
	python3 -m venv venv
	./venv/bin/python3 -m pip install poetry
	./venv/bin/python3 -m poetry env use python3.10
	./venv/bin/python3 -m poetry install
	touch .installed

debug: install
	python3 -m pdb a_maze_ing.py

clean:
	-rm __pycache__ -r
	-rm .mypy_cache -r
	-rm .installed
	-rm venv -r
	-rm dist -r

lint: install
	-./venv/bin/python3 -m poetry run flake8 mazegen/ a_maze_ing.py 
	-./venv/bin/python3 -m poetry run mypy mazegen/ a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build: install
	./venv/bin/python3 -m poetry build

lint-strict: install
	-./venv/bin/python3 -m poetry run flake8 mazegen/ a_maze_ing.py
	-./venv/bin/python3 -m poetry run mypy --strict mazegen/ a_maze_ing.py
