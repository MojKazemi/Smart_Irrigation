import json
import requests
import paho.mqtt.client as PahoMQTT
import paho.mqtt.publish as paho_mqtt_publish


class MyMQTT:
    def __init__(self, clientID, broker, port, notifier, username = None, password = None,_transport="tcp"):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.clientID = clientID
        self._topic = ""
        self._isSubscriber = False
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, True, transport=_transport)
        if username != None: self._paho_mqtt.username_pw_set(username,password)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        self.notifier.notify(msg.topic, msg.payload)

    def myPublish(self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)

    def mySubscribe(self, topic):

        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        print("subscribed to %s" % (topic))

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

    def stop(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
    
class MyRequest:
    def __init__(self,web_server = '127.0.0.1', web_server_port = '8080'):
        # self._server = web_server
        # self._server_port = web_server_port
        self._root = f'http://{web_server}:{web_server_port}'

    def get_broker(self):
        catalog_broker = requests.get(f'{self._root}/catalog/broker_details').json()
        return catalog_broker['broker'], catalog_broker['port'], catalog_broker['baseTopic']

    def get_catalog(self):
        catalog_user = requests.get(f'{self._root}/catalog/user_details').json()
        return catalog_user

    def get_catalog_farm(self):
        catalog_farm = requests.get(f'{self._root}/catalog/farm_details').json()
        return catalog_farm

    def get_threshold(self,IDs):

        thresh = requests.get(
            f'{self._root}/catalog/threshold?farmID={IDs["farm"]}&sectionID={IDs["section"]}').json() 
        return thresh

    def get_status(self,IDs):
        status = requests.get(f'{self._root}/catalog/pump_status/?farmID={IDs["farm"]}&sectionID={IDs["section"]}').json()
        return status

    def put_status(self,IDs, status):
        requests.put(f'{self._root}/catalog/pump_status/?farmID={IDs["farm"]}&sectionID={IDs["section"]}&status={status}')
    
    def get_TS_chID(self,farmID,secID):
        chID = requests.get(f'{self._root}/catalog/channelID?farmID={farmID}&sectionID={secID}').json()
        _chID = chID['ch_ID']
        return _chID

    def get_control_status(self,IDs):
        _status = requests.get(f'{self._root}/catalog/control_status/?farmID={IDs["farm"]}&sectionID={IDs["section"]}').json()
        return _status

    def post_status(self,IDs, status):
        requests.post(f'{self._root}/statistics/pump_status?farmID={IDs["farm"]}&sectionID={IDs["section"]}&status={status}')

    def get_manual_schedul(self,IDs):
        _schedul = requests.get(f'{self._root}/catalog/manual_schedul/?farmID={IDs["farm"]}&sectionID={IDs["section"]}').json()
        return _schedul

class ts_publish:
    def __init__(self, channel_ID = "2073420", ts_conf = 'ts_conf.json'):
        self.channel_ID = channel_ID
        with open(ts_conf, 'r') as file:
            conf = json.load(file)
        self.mqtt_host = conf['host']
        self.mqtt_client_ID = conf['client_ID']
        self.mqtt_username  = conf['username']
        self.mqtt_password  = conf['password']
        self.t_transport = conf['t_transport']
        self.t_port = conf['t_port'] 
        self.client = MyMQTT(self.mqtt_client_ID,
                            self.mqtt_host,
                            self.t_port,None,
                            username=self.mqtt_username,
                            password=self.mqtt_password,
                            _transport= self.t_transport)

    def tsSinglePublish(self, payload):
        topic = "channels/" + self.channel_ID + "/publish"
        print ("Writing Payload = ", payload," to host: ", self.mqtt_host, " clientID= ", self.mqtt_client_ID, " User ", self.mqtt_username, " PWD ", self.mqtt_password)
        paho_mqtt_publish.single(topic, payload,
            hostname=self.mqtt_host, transport=self.t_transport,
            port=self.t_port, client_id=self.mqtt_client_ID,
            auth={'username':self.mqtt_username,'password':self.mqtt_password})

    def tsPublish(self, payload):
        topic = "channels/" + self.channel_ID + "/publish"
        self.client.myPublish(topic,payload)
        print ("Writing Payload = ", payload," to host: ", self.mqtt_host, " clientID= ", self.mqtt_client_ID)

    def start(self):
        self.client.start()

