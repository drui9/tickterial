import time
import json
from tickterial import app
from flask import Response, redirect, url_for, render_template


def events():
	for i in range(1000):
		time.sleep(1)
		yield f'{json.dumps({"data": i})}\n\n'.encode('utf8')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/stream')
def stream():
	return Response(events(), content_type='text/event-stream')


@app.route('/subscribe', methods=['POST'])
def subscribe():
	return redirect(url_for('stream'))
