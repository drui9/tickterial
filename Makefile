SRC := start.py
TSRC := tests.py

test: $(TSRC)
	./venv/bin/python3 tests.py

run: $(SRC)
	./venv/bin/python3 $^

build:
	./venv/bin/python3 -m build

clean:
	rm -rf dist build *.egg-info **/__pycache__

