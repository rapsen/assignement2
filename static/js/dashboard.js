const socket = io();

        socket.on('update', function(message) {
            id = document.getElementById("select").value
            if (message.deviceId == id)
            {
                document.getElementById("time").innerHTML = message.time;
                document.getElementById("state").innerHTML = message.state;
                let s;

                switch (message.state) {
                    case 'READY-PROCESSING-EXECUTING':
                    case 'READY-PROCESSING-ACTIVE':
                        s = "processing";
                        break;
                    case 'READY-IDLE-STARVED':
                    case 'READY-IDLE-BLOCKED':
                        s = "idle";
                        break;
                    default:
                    s = "error";
                }

                document.getElementById("status").src = "../static/icons/"+s+".png";

            };
        });

function ask(select){
    socket.emit("ask", select.value)
}
    