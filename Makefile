SRC := start.py
TSRC := test.py


run: $(SRC)
	./venv/bin/python3 $^

test: $(TSRC)
	./$<

build:
	./venv/bin/python3 -m build

clean:
	rm -rf dist *.egg-info **/__pycache__
