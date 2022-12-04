const socket = io();

socket.on('update', function (message) {
    id = document.getElementById("select").value;
    if (message.deviceId == id) {
        document.getElementById("time").valueAsDate = time(message.time);
        document.getElementById("state").innerHTML = message.state;
        document.getElementById("status").src = "../static/icons/" + message.state + ".png";
    };
});
 
$(document).ready()
{
    var t = document.getElementById('time').value
    console.log(t)
    document.getElementById('time').value = time(t);
}

function time(ts) {
    let time = new Date(ts*1000)
    time.setHours(new Date(ts*1000).getHours() + 4) // Adapt to GMT+2 time
    return time;
}

function ask(select) {
    socket.emit("ask", select.value)
}
