.PHONY: test-reqs package selftest fmt lint local_install dev_install test coverage clean push_pypi


test-reqs:
	pip install -r test-requirements.txt

package:
	python3 setup.py bdist_wheel

selftest:
	./run_selftest.sh

fmt: test-reqs
	black pls --config ./pls/pyproject.toml

lint: test-reqs
	pylama -o ./pls/pylama.ini pls/

local_install:
	pip install -r requirements.txt
	pip install .

dev_install: test-reqs
	pip install -e . --quiet

clean:
	rm -rf build dist pls.egg-info htmlcov

# Need to configure .pypirc with credentials
push_pypi: test-reqs
	python3 -m twine upload --repository plsbuild dist/*
