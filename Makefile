SRC := wsgi.py
TSRC := test.py

run: $(SRC)
	venv\Scripts\python $^

test: $(TSRC)
	venv\Scripts\python $<

install:
	venv\Scripts\pip install -r requirements.txt

build:
	venv\Scripts\python -m build

clean:
	rm -rf dist build *.egg-info **/__pycache__
