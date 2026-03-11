run: venv
	./venv/bin/python3 main.py

venv: install

install: .installed

.installed:
	python3 -m venv venv
# 	./venv/bin/python3 -m pip install ./mlx_CLXV/python/dist/mlx-2.2-py3-none-any.whl
	touch .installed
# 	./venv/bin/python3 -m pip install mlx.whl

debug: install
	python3 -m pdb main.py

clean:
   # Remove temporary files or caches (e.g., __pycache__, .mypy_cache)
	-rm __pycache__ -r
	-rm .mypy_cache -r
	-rm venv -r
	-rm dist -r

lint: install
	-./venv/bin/python3 -m flake8 mazegen/ main.py 
	-./venv/bin/python3 -m mypy mazegen/ main.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build: install
	./venv/bin/python3 -m build --wheel --outdir dist/

lint-strict: install
	-./venv/bin/python3 -m flake8 mazegen/ main.py
	-./venv/bin/python3 -m mypy --strict mazegen/ main.py
