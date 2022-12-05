const socket = io();

socket.on('update', function (message) {
    if (message.deviceId == document.getElementById("id").value) {
        console.log(time(message.time))
        document.getElementById("time").innerHTML = time(message.time);
        document.getElementById("state").innerHTML = message.state;
        document.getElementById("status").src = "../static/icons/" + message.state + ".png";
    };
});
 

function time(ts) {
    let time = new Date(ts*1000);
    time.setHours(new Date(ts*1000).getHours() + 2) // Adapt to GMT+2 time
    return time.toLocaleString('en-UK')
}