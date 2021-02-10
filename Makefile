.PHONY: create-virtual-env
create-virtual-env:
	python -m venv ./venv

.PHONY: build-deps
build-deps: create-virtual-env
	./venv/bin/pip install -r requirements.txt

.PHONY: run
run: build-deps
	./venv/bin/uvicorn CTFe.main:app --reload

.PHONY: test
test: build-deps
	./venv/bin/pytest
