import json
import pdb

def cut_space(a_str):
	index = a_str.index(' ')
	return a_str[0: index]

def parse_file(filename, list_of_rooms):
	reader = open(filename, 'r')
	ending_line = reader.seek(0, 2)
	reset = reader.seek(0)
	while reader.tell() < ending_line:
		# pdb.set_trace()
		
		next_line = reader.readline()
		if next_line != "" and " " in next_line:
			next_line = cut_space(next_line)
			list_of_rooms.append(next_line)
	reader.close()

def main():
	rooms = []
	with open('../json/buildings.json', 'r') as f:
		building_list = json.load(f)
	print(building_list)
	
	for building in building_list:
		print("Parsing data for" + building + "...")
		source = '../textfiles/' + building + '.txt'
		parse_file(source, rooms)

	writer = open('../json/rooms.json', 'w')

	writer.write(str(rooms))
	writer.close()

main()
