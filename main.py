from config import *
from controller import mqtt, socket
from views import app

# Attach to the app the mqtt client and the socket
mqtt.init_app(app)
socket.init_app(app)


print(f"Suscribed to {MQTT_TOPIC} from {BROKER_HOSTNAME}:{BROKER_PORT}")

mqtt.subscribe(MQTT_TOPIC)

if __name__ == "__main__":

    socket.run(app, debug=True)
