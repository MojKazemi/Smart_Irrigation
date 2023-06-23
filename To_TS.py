import json, time
from MyMQTT_Reqs import MyMQTT, MyRequest
import requests
import paho.mqtt.publish as paho_mqtt_publish

class ts_publish:
    def __init__(self, ts_conf = 'ts_conf.json'):
        # self.channel_ID = channel_ID
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

    def tsSinglePublish(self, payload, channel_ID= "2073420"):
        topic = "channels/" + channel_ID + "/publish"
        # print ("Writing Payload = ", payload," to host: ", self.mqtt_host, " clientID= ", self.mqtt_client_ID, " User ", self.mqtt_username, " PWD ", self.mqtt_password)
        paho_mqtt_publish.single(topic, payload,
            hostname=self.mqtt_host, transport=self.t_transport,
            port=self.t_port, client_id=self.mqtt_client_ID,
            auth={'username':self.mqtt_username,'password':self.mqtt_password})

    def tsPublish(self, payload, channel_ID= "2073420"):
        topic = "channels/" + channel_ID + "/publish"
        self.client.myPublish(topic,payload)
        # print ("Writing Payload = ", payload," to host: ", self.mqtt_host, " clientID= ", self.mqtt_client_ID)

    def start(self):
        self.client.start()

class To_TS:
    def __init__(self, userID,ts_conf='./ts_conf.json'):
        with open(ts_conf, 'r') as file:
            se_conf = json.load(file)

        self.rc_add = se_conf["rc_address"]
        self.rc_port = se_conf["rc_port"]

        broker_conf = requests.get(f'http://{self.rc_add}:{self.rc_port}/services/broker').json()
       
        self.my_req = MyRequest()
        # broker, port, self.basetopic = self.my_req.get_broker()
        self.topic = f'{broker_conf["baseTopic"]}/data/#'
        self.client = MyMQTT(
            userID,
            broker_conf["broker"], 
            broker_conf["port"], 
            notifier=self
            )
        # self.ts_chID = TS_channelID
        self.publish_TS = ts_publish(ts_conf=ts_conf)


    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
        self.publish_TS.start()

    def stop(self):
        self.stop()

    def notify(self, topic, message):
        msg = json.loads(message)
        # print(f'Received message :\n{msg}\nfrom topic: {topic}\n')
        
        for msg_event in msg['e']:
            if msg_event['n'] == 'Temperature':
                TS_field = 'field1'
            else:
                TS_field = 'field2'
            sensor_value = msg_event['value']
        
        farmID = msg['farmID']
        secID  = msg['sectionID']
        
        # Thingspeak Broker
        payload = f"&{TS_field}=" + str(sensor_value)
        # print(payload)
        try:
            # ch_ID = my_req.get_TS_chID(farmID,secID)
            ch_ID = requests.get(f'http://{self.rc_add}:{self.rc_port}/catalog/channelID?farmID={farmID}&sectionID={secID}').json()
            # print(f'ch_ID :{ch_ID}')
            self.publish_TS.tsPublish(payload, channel_ID = ch_ID['ch_ID'])
        except Exception as e:
            print(f'the error is happend {e}')
            

if __name__ == "__main__":
    
    to_ts = To_TS("To_ThingSpeak",ts_conf='./ts_conf.json')
    to_ts.start()
    
    while True:
        time.sleep(2)