env := .venv
test_src := test.py

dl:
	@.venv/bin/tickterial --symbols GBPUSD EURUSD USDJPY XAUUSD --start '2024-04-08 17:00:00' --end '2024-04-10 00:00:00' --progress true

test: $(test_src) $(env)
	$(env)/bin/python $<

install: $(env)
	$</bin/pip install -e .

$(env):
	python -m venv $@

clean:
	rm -rf dist build *.egg-info **/__pycache__

