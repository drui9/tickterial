SRC := start.py
TSRC := test.py

test: $(TSRC)
	./$<

run: $(SRC)
	./venv/bin/python3 $^

build:
	./venv/bin/python3 -m build

clean:
	rm -rf dist *.egg-info **/__pycache__
