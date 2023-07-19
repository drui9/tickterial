import json
from tickterial import app
from flask import Response, request, redirect, url_for


@app.route('/stream', methods=['GET', 'POST'])
def stream():
	if request.headers.get('Content-Type') == 'text/event-stream':
		def gen_data():
			for i in range(10):
				yield f'{json.dumps({"data": i})}\n\n'.encode('utf8')
		return Response(gen_data(), mimetype='event-stream')
	return {'ok': True}

@app.route('/subscribe', methods=['POST'])
def subscribe():
	return redirect(url_for('stream'))
