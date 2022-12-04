from config import *
from controller import mqtt, socket
from views import app

# Attach to the app the mqtt client and the socket
mqtt.init_app(app)
socket.init_app(app)

mqtt.subscribe(MQTT_TOPIC)
log.info(f"MQTT Suscribed to {MQTT_TOPIC} from {BROKER_HOSTNAME}:{BROKER_PORT}")

if __name__ == "__main__":

    socket.run(app, debug=True)
