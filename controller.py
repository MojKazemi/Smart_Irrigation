import json, time, datetime
from MyMQTT_Reqs import MyMQTT, MyRequest
import requests

class MoistController:
    def __init__(self,userID):
        self.my_req = MyRequest()
        broker, port, baseTopic = self.my_req.get_broker()
        self.baseTopic = baseTopic
        self.topic = f'{baseTopic}/#'
        self.temp_values = []
        self.mois_values = []
        self.pre_times = 5
        self.status = ''
        self.IDs={'user':'','farm':'','section':''}
        self.client = MyMQTT(userID,broker, port,notifier=self)
        
    
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)       

    def stop(self):
        self.stop()

    def notify(self, topic, message):
        msg = json.loads(message)
        
        self.IDs['user'] = msg['userID']
        self.IDs['farm'] = msg['farmID']
        self.IDs['section'] = msg['sectionID']

        if msg['e']['n'] == 'Temperature':
            tmp_value = msg['e']['value']
            self.temp_values.append(tmp_value)
        elif msg['e']['n'] == 'Soil_Moisture':
            mois_value = msg['e']['value']
            self.mois_values.append(mois_value)

        if len(self.temp_values) == len(self.mois_values) and len(self.mois_values) >1:
            self.ControlServo(self.temp_values, self.mois_values)

    def ControlServo(self,temp_values, mois_values):
        if len(temp_values) > self.pre_times:
            temp_values.pop(0)
            mois_values.pop(0)
        mean_temp = sum(temp_values)/len(temp_values)
        mean_mois = sum(mois_values)/ len(mois_values)

        thresh = self.my_req.get_threshold(self.IDs)
        thresh['temp'], thresh['mois_min'], thresh['mois_max']
        print(f'Temp Thresh:{thresh["temp"]}  Mois min Thresh:{thresh["mois_min"]} Mois max Thresh:{thresh["mois_max"]}')
        print(f'mean Temp:{mean_temp}   mean Mois: {mean_mois}')

        if mean_mois > thresh["mois_min"]:
            if mean_mois < thresh["mois_max"]:
                if mean_temp > thresh["temp"]:
                    self.status = 'on'
                else:
                    self.status = 'off'
            else:
                self.status = 'off'
        else:
            self.status = 'on'

        prev_status = self.my_req.get_status(self.IDs)

        if self.status != prev_status:
            self.my_req.put_status(self.IDs,self.status)
            print(f'------>>>> become {self.status} <<<<<--------')
            self.sendActStatus(self.status)

    def sendActStatus(self, pump_state):
        topic = '/'.join([self.baseTopic, self.IDs['user'], self.IDs['farm'],
                              self.IDs['section'], 'Devices', 'Pump_status'])
        print(topic)
        __message = {
            'userID': self.IDs['user'],
            'farmID': self.IDs['farm'],
            'sectionID': self.IDs['section'],
            'bn': '',
            'e': {'n': '', 'value': '', 'timestamp': '', 'unit': ''}
        }
        __message['bn'] = topic
        __message['e']['n'] = 'pump'
        __message['e']['value'] = pump_state
        __message['e']['timestamp'] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        __message['e']['unit'] = 'boolean'
        
        self.client.myPublish(topic, __message)
      
        self.my_req.post_status(self.IDs, pump_state)
        

if __name__ == "__main__":
    
    test = MoistController("hh")
    test.start()
    
    while True:
        time.sleep(1)
    