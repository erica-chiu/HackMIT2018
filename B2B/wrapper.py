import outdoors
from importlib import reload
reload(outdoors)

# Functions required by ui.js
def find_shortest_path(d):
	return outdoors.shortest_path(d['start_building'], d["end_building"], d['start_floor'], d['end_floor'])

def get_route_description(d):
	return outdoors.generate_instructions(d['path'])
	