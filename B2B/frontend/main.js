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
	invoke_rpc("/find_shortest_path", args, 50000);

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

	var input_data = {  "start_buildling": dept_building,
											"end_building": dest_building,
											"start_floor": initial_floor,
											"end_floor": final_floor };
	return input_data;
}

// Python-related functions(to connect with python)
function load_resource(name) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
    }
  }
  xhr.send();
}

function invoke_rpc(method, args, timeout){
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  console.log('opened');
  xhr.setRequestHeader('Content-Type','application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  console.log("we are here");
  xhr.onloadend = function() {
  	console.log('hello!');
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText)
      $("#timeout").hide();
     	console.log(result);
  	}
	}
}

function restart(){
  invoke_rpc( "/restart", {} );
}

function main(){
	// Code that runs first
	$(document).ready(function(){
	    // race condition if init() does RPC on function not yet registered by restart()!
	    //restart();
	    //init();
	    invoke_rpc( "/restart", {}, 0, function() { console.log('initialization!'); } )
	});
	eventListener();
}

main();