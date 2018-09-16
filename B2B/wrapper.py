from flask import Flask, render_template, request, jsonify
import outdoors
import pdb
import sys

app = Flask(__name__)

@app.route('/find_shortest_path', methods=['POST'])
def find_shortest_path():
	d = request.form
	print(d, file=sys.stderr)
	return jsonify(outdoors.shortest_path(d['start_building'], d["end_building"], d['start_floor'], d['end_floor']))

@app.route('/')
def render_HTML():
	return render_template('index.html')

