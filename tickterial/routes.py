import json
from flask import Response, request
from tickterial import app, tickloader

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.headers.get('Content-Type') == 'text/event-stream':
		def gen_data():
			for i in range(10):
				yield f'{json.dumps({"data": i})}\n'.encode('utf8')
		return Response(gen_data(), mimetype='event-stream')
	return {'ok': True}
