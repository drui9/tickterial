SRC := start.py
TSRC := tests.py

test: $(TSRC)
	venv\Scripts\python tests.py

run: $(SRC)
	venv\Scripts\python $^

build:
	venv\Scripts\python -m build

clean:
	rm -rf dist build *.egg-info **/__pycache__

