var socket = io();

// On connect, let server know
socket.on('connect', function() {
    socket.emit('connected_event', {data: 'Connected!'});
});

// When receiving a drowsy alert, activate the onDrowsey function
socket.on('drowsy_alert', (data) => {
    onDrowsy(data);
});

// For receiving end of ride data
// socket.on('end_ride_data', (data) => {
// TODO
// });

var numDrowsy = 0; // Number of drowsy occurances per 30 seconds
var graphLabels = [];
var graphData = [];

// Called on simulated/genuine drowsy event
function onDrowsy(data) {
    // Get the time of drowsiness
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    const time = hours + ":" + minutes + ":" + seconds;

    // Increment the number of drowsy occurances
    numDrowsy++;

    // Get the notification list
    var ul = document.getElementById("notiflist");

    // Create a new list element
    var li = document.createElement("li");
    li.appendChild(document.createTextNode("Drowsy at " + time));

    // Add it to the list
    ul.appendChild(li);

    // Get the Notification divider
    var notifDiv = document.getElementById("notifsdiv");

    // Make sure to be scrolled to bottom
    notifDiv.scrollTop = notifDiv.scrollHeight;

    // If alarm is activated, play alarm
    var alarmCheck = document.getElementById("alarmtoggle");
    if(alarmCheck.checked) {
        var alarmsound = new Audio("/static/sounds/alarm.mp3");
        alarmsound.play();
    }
}

// Tell the server that the ride is over
function endRide() {
    socket.emit("end_ride");
}

function updateGraphData() {
    var ctx = document.getElementById('drowsy_graph');

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const time = hours + ":" + minutes + ":" + seconds;

    graphLabels.push(time);
    graphData.push(numDrowsy);

    var labels = graphLabels;
    var data = graphData;

    // Reset numDrowsy
    numDrowsy = 0;
    var drowsy_graph = new Chart(ctx,
    {
        type:"line",
        data:
        {
            "labels":labels,
            "datasets":[{
                "label":"Drowsy Occurrances",
                "data":data,
                "fill":false,
                "borderColor":"rgb(75, 192, 192)",
                "lineTension":0.1
            }]
        },
        options:{}
    });
}

// Update the graph every 30 seconds
setInterval(updateGraphData, 30 * 1000);

// Function to swap the drowsy notifications with graph
function SwapNotifGraph()
{
    const graphDivider = document.getElementById("graphdiv");
    const notifDivider = document.getElementById("notifsdiv");

    let btn = document.getElementById("swapbutton");

    // Notif divider hidden
    if( notifDivider.style.display == "none" )
    {
        graphDivider.style.display = "none";
        notifDivider.style.display = "block";
        btn.innerHTML = "Show Graph";
    }
    else // Graph divider hidden
    {
        graphDivider.style.display = "block";
        notifDivider.style.display = "none";
        btn.innerHTML = "Show Notifications";
    }
}