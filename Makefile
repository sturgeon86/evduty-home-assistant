.PHONY : install test coverage release

install:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

test:
	ruff . && \
	python3 -m unittest

coverage:
	coverage run --branch -m unittest
	coverage html

release:
	.github/release.sh ${bump}
