function eventListener() {
	var submit = document.getElementById('submit');
	submit.addEventListener("click", function(){
		console.log('button is clocked!');
		if (document.getElementById('errPara') !== null){
			document.getElementById('errPara').remove();
		}
		readInput();
	});
}


function readInput() {
	console.log('Entering readInput');
	var deptElement = document.getElementById('dept');
	var departureRoom = deptElement.value.toString();
	console.log(departureRoom)
	deptElement.value = "";

	var destElement = document.getElementById('dest');
	var destinationRoom = destElement.value.toString();
	console.log(destinationRoom)
	destElement.value = ""

	var maxFloorElement = document.getElementById('max_floor');
	var maxFloorTolerance = maxFloorElement.value;
	console.log(maxFloorTolerance)
	maxFloorElement.value = ""

	args = parseInputForShortestPath(departureRoom, destinationRoom, maxFloorTolerance);
	console.log(args);
	
	instructions = makeRequest(args);
	console.log(instructions);
	return instructions
}

function parseInputForShortestPath(dept, dest, max_floor){
	var initial_floor = 1;
	var final_floor = 1;
	if (dept.includes("-")){
		dept_building = dept.substring(0, dept.indexOf("-"));
		initial_floor = parseInt(dept.substring(dept.indexOf("-")+1, dept.indexOf("-")+2));
	}

	if (dest.includes("-")){
		dest_building = dest.substring(0, dest.indexOf("-"));
		final_floor =  parseInt(dest.substring(dest.indexOf("-")+1, dest.indexOf("-")+2));
	}

	var input_data = {  "start_building": dept_building,
											"end_building": dest_building,
											"start_floor": initial_floor,
											"end_floor": final_floor };
	return input_data;
}

function makeRequest(input){
	return_data = 0
	$.ajax({
		type: 'POST',
		url: '/find_shortest_path',
		data: input,
	}).done(function(data){
		console.log(data)
		return_data = data
		instructionDiv = document.getElementById('instruction');
		instructionDiv.innerText = data;
	});
	return return_data;
}

function main(){
	// Code that runs first
	eventListener();
}

main();