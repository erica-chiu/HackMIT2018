function eventListener() {
	var submit = document.getElementById('submit');
	submit.addEventListener("click", function(){
		console.log('button is clocked!');
		readInput()
	});
}



function readInput() {
	console.log('Entering readInput');
	var dept_element = document.getElementById('dept');
	var departure_room = dept_element.value;
	dept_element.value = "";

	var dest_element = document.getElementById('dest');
	var destination_room = dest_element.value;
	dest_element.value = ""
}

function main(){
	eventListener()
}

main()