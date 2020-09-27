var socket = io();
socket.on('drowsy_alert', (data) => {
    onDrowsy(data);
});

socket.on('graph_data', (data) => {
    onGraphData(data);
});


// socket.on('end_ride_data', (data) => {

// });

var numDrowsy = 0;
var graphLabels = [];
var graphData = [];

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

    // If alarm
    var alarmCheck = document.getElementById("alarmtoggle");
    if(alarmCheck.checked) {
        var alarmsound = new Audio("/static/sounds/alarm.mp3");
        alarmsound.play();
    }
}

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

// Call updateGraphData every 30 seconds
setInterval(updateGraphData, 30 * 1000);

function SwapNotifGraph()
{
    var d1 = document.getElementById("graphdiv");
    var d2 = document.getElementById("notifsdiv");

    var btn = document.getElementById("swapbutton");

    // Notif divider hidden
    if( d2.style.display == "none" )
    {
        d1.style.display = "none";
        d2.style.display = "block";
        btn.innerHTML = "Show Graph";
    }
    else // Graph divider hidden
    {
        d1.style.display = "block";
        d2.style.display = "none";
        btn.innerHTML = "Show Notifications";

    }
}