import paho.mqtt.client as mqtt
import logging
import time


class MQTT:

    def __init__(self, broker, port, client_id, username, password):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize MQTT client for MQTT version 5
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_log = self.on_log

        self.is_connected = False

    def on_connect(self, client, userdata, flags, reasonCode, properties):
        if reasonCode == 0:
            self.logger.info("Connected to broker")
            self.is_connected = True
        else:
            self.logger.error(f"Connection failed with reason code {reasonCode}")

    def on_disconnect(self, client, userdata, reasonCode, properties):
        self.is_connected = False
        if reasonCode != 0:
            self.logger.warning(f"Unexpected disconnection with reason code {reasonCode}")
            self.reconnect()

    def on_message(self, client, userdata, msg):
        self.logger.info(f"Received message: {msg.topic} -> {msg.payload.decode()}")

    def on_subscribe(self, client, userdata, mid, granted_qos, properties):
        self.logger.info(f"Subscribed: {mid} {granted_qos}")

    def on_unsubscribe(self, client, userdata, mid, properties, reasonCodes):
        self.logger.info(f"Unsubscribed: {mid}")

    def on_log(self, client, userdata, level, buf):
        self.logger.info(f"Log: {buf}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=100, clean_start=True)
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self.reconnect()

    def reconnect(self):
        while not self.is_connected:
            self.logger.info("Reconnecting...")
            try:
                self.client.reconnect()
                self.is_connected = True
            except Exception as e:
                self.logger.error(f"Reconnection error: {e}")
            time.sleep(5)

    def start(self):
        self.connect()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, payload, qos=0, retain=False, properties=None):
        try:
            self.client.publish(topic, payload, qos, retain, properties)
            self.logger.info(f"Published: {topic} -> {payload}")
        except Exception as e:
            self.logger.error(f"Publish error: {e}")

    def subscribe(self, topic, qos=0, options=None, properties=None):
        try:
            self.client.subscribe(topic, qos, options, properties)
            self.logger.info(f"Subscribed to topic: {topic}")
        except Exception as e:
            self.logger.error(f"Subscribe error: {e}")

    def unsubscribe(self, topic, properties=None):
        try:
            self.client.unsubscribe(topic, properties)
            self.logger.info(f"Unsubscribed from topic: {topic}")
        except Exception as e:
            self.logger.error(f"Unsubscribe error: {e}")
