const socket = io();

socket.on('update', function (message) {
    id = document.getElementById("select").value
    if (message.deviceId == id) {
        document.getElementById("time").innerHTML = message.time;
        document.getElementById("state").innerHTML = message.state;
        document.getElementById("status").src = "../static/icons/" + message.state + ".png";
    };
});

function ask(select) {
    socket.emit("ask", select.value)
}
