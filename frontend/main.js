async function loadData(filename){
	loadJSon(filename, async function(response){
		var actual_JSON = JSON.parse(response);
		console.log(actual_JSON);
		await new Promise(resolve => setTimeout(resolve, 3000));
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

function eventListener(building_set, room_set) {
	var submit = document.getElementById('submit');
	submit.addEventListener("click", function(){
		console.log('button is clocked!');
		if (document.getElementById('errPara') !== null){
			document.getElementById('errPara').remove();
		}
		readInput(building_set, room_set);
	});
}


function readInput(building_set, room_set) {
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

}

function findShortestPath(start, destination){
	
}

function main(){
	eventListener(building_data, room_data);
}

main()