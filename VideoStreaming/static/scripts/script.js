function onDrowsy() {
    // Get the time of drowsiness
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    const time = hours + ":" + minutes + ":" + seconds;

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