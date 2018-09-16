function loadData(filename){
	loadJSon(filename, function(response){
		var actual_JSON = JSON.parse(response);
		console.log(actual_JSON);
		return actual_JSON
	});
}

function loadJSon(filename, callback){
	var xobj = new XMLHttpRequest();
	xobj.overrideMimeType("application/json");
	xobj.open('GET', filename, true);
	xobj.onreadystatechange = function() {
		if (xobj.readyState == 4 && xobj.status == "200"){
			callback(xobj.responseText);
		}
	};
	xobj.send(null);
}

function callbackSuccess() {
	console.log('Data load is successful.');
}

function eventListener() {
	var submit = document.getElementById('submit');
	submit.addEventListener("click", function(){
		console.log('button is clocked!');
		readInput()
	});
}


function readInput() {
	console.log('Entering readInput');
	var deptElement = document.getElementById('dept');
	var departureRoom = deptElement.value;
	deptElement.value = "";

	var destElement = document.getElementById('dest');
	var destinationRoom = destElement.value;
	destElement.value = ""

	var maxFloorElement = document.getElementById('max_floor');
	var maxFloorTolerance = maxFloorElement.value;
	maxFloorTolerance.value = ""

	/*
	if (checkInputValidity(departureRoom, destinationRoom, maxFloorTolerance)){
		// Make function calls to the python.
	}
	else{
		// Append a reminder that there is an error.
	}
	*/
}

function checkInputValidity(start, end, max_floor) {

}

function inputErrorWarning(){

}

function main(){
	const building_dir = "../json/buildings.json";
	const room_dir = "../json/rooms2.json";
	var building_data = loadData(building_dir);
	var room_data = loadData(room_dir);
	eventListener();
}

main()