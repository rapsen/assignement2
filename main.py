from config import *
from controller import mqtt, socket, subscribe
from views import app

# Config flask application
app.config.update(CONFIG)

# Attach to the app the mqtt client and the socket
mqtt.init_app(app)
socket.init_app(app)


subscribe()

if __name__ == "__main__":
    socket.run(app, debug=True)
