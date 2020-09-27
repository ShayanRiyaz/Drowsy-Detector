var directionsService;
var directionsRenderer;
var map;

function initMap() {
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    var chicago = new google.maps.LatLng(41.850033, -87.6500523);
    var mapOptions = {
      zoom:7,
      center: chicago
    }
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    directionsRenderer.setMap(map);
}

function calcRoute(start, end) {
    var request = {
        origin: start,
        destination: end,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(result, status) {
        if (status == 'OK') {
        directionsRenderer.setDirections(result);
        }
    });
}



var socket = io();

// On connect, let server know
socket.on('connect', function() {
    socket.emit('connected_event', {data: 'Connected!'});
});

// When receiving a drowsy alert, activate the onDrowsey function
socket.on('drowsy_alert', (data) => {
    onDrowsy(data);
});

socket.on('no_location', () =>{
    // Get the notification list
    var ul = document.getElementById("notiflist");

    // Create a new list element
    var li = document.createElement("li");
    li.appendChild(document.createTextNode("No route available for these locations, Try again."));

    // Add it to the list
    ul.appendChild(li);

    // Get the Notification divider
    var notifDiv = document.getElementById("notifsdiv");

    // Make sure to be scrolled to bottom
    notifDiv.scrollTop = notifDiv.scrollHeight;
});

socket.on('location', (data) => {
    // console.log(data);
    simulate_user(data);
});

socket.on('nearby_locations', (data) => {
    console.log(data.data);
    for(let i = 1; i < Object.keys(data.data).length; i++){
        let current_location = data.data[i];
        let current_lat = current_location.loc.lat;
        let current_lon = current_location.loc.lng;
        let current_name = current_location.name;
        let current_open_status = current_location.open;

        let infoStr = current_open_status;
        let titleStr = current_name;
        draw_info_window(current_lat, current_lon, infoStr, titleStr);
    }
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

var userLon = 0;
var userLat = 0;
async function simulate_user(data){
    let coords = data.data;
    console.log(coords.length);
    console.log(coords);
    for(let i = 0; i < coords.length; i+=50){
        let current_lat = coords[i][0];
        let current_lon = coords[i][1];
        userLat = current_lat;
        userLon = current_lon;
        draw_marker(current_lat,current_lon);
        sleep(10000);
    }
}


function draw_marker(lat,lng){
    let myLatlng = new google.maps.LatLng(lat,lng);
    let marker = new google.maps.Marker({
        position: myLatlng,
        title:"Hello World!"
    });
    marker.setMap(map);
}

function draw_info_window(lat, lng, infoStr, titleStr){
    let infowindow = new google.maps.InfoWindow({
        content: "<div>" + titleStr + " is open to visit!" + "<br> Stay Safe, Take a break" + "</div>"
      });

    let myLatlng = new google.maps.LatLng(lat,lng);
    let marker = new google.maps.Marker({
        position: myLatlng,
        map,
        title: titleStr
    });
    marker.addListener('click', function() {
        infowindow.open(map, marker);
      });    
}

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

    const user_data = {
        userLon: userLon,
        userLat: userLat
    }
    socket.emit('user_location', user_data);
    
    // If alarm is activated, play alarm
    var alarmCheck = document.getElementById("alarmtoggle");
    if(alarmCheck.checked) {
        var alarmsound = new Audio("/static/sounds/alarm.mp3");
        alarmsound.play();
    }
}



// // Tell the server that the ride is over
// function endRide() {
//     calcRoute()
//     // socket.emit("end_ride");
// }

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

function submit_location(){
    const start_location = document.getElementById("startlocation").value;
    const end_location = document.getElementById("endlocation").value;
    calcRoute(start_location,end_location);
    data = {
        start_location: start_location,
        end_location: end_location
    }
    socket.emit("location_data", data);
}