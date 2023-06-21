import json, time
from MyMQTT_Reqs import ts_publish, MyMQTT, MyRequest
import requests

class To_TS:
    def __init__(self, userID, TS_channelID=''):
        self.my_req = MyRequest()
        broker, port, self.basetopic = self.my_req.get_broker()
        self.topic = f'{self.basetopic}/data/#'
        self.client = MyMQTT(userID,broker, port, notifier=self)
        self.ts_chID = TS_channelID
        self.publish_TS = ts_publish(ts_conf='ts_conf.json')


    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
        self.publish_TS.start()

    def stop(self):
        self.stop()

    def notify(self, topic, message):
        msg = json.loads(message)
        print(f'Received message :\n{msg}\nfrom topic: {topic}\n')
        
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
        ch_ID = my_req.get_TS_chID(farmID,secID)
        self.publish_TS.tsPublish(payload, channel_ID = ch_ID)

if __name__ == "__main__":
    
    my_req = MyRequest()
    to_ts = To_TS("To_ThingSpeak")
    to_ts.start()
    
    while True:
        time.sleep(1)