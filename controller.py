import json, time, datetime
from MyMQTT_Reqs import MyMQTT, MyRequest
import requests

class MoistController:
    def __init__(self,userID):
        self.my_req = MyRequest()
        broker, port, baseTopic = self.my_req.get_broker()
        self.baseTopic = baseTopic
        self.topic = f'{baseTopic}/data/#'
        self.temp_values = []
        self.mois_values = []
        self.pre_times = 5
        self.status = ''
        self.IDs={'user':'','farm':'','section':''}
        self.client = MyMQTT(userID,broker, port,notifier=self)
        self.telegram_message={"alert":"", "farm":"", "section":""}
        self.alarm_topic = f'{baseTopic}/alarm/'
        
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)       

    def stop(self):
        self.stop()

    def notify(self, topic, message):
        msg = json.loads(message)
        
        # self.IDs['user'] = msg['userID']
        self.IDs['farm'] = msg['farmID']
        self.IDs['section'] = msg['sectionID']
        self.my_req.put_sen_val(self.IDs, msg['e']['n'], msg['e']['value'])

        control_status = self.my_req.get_control_status(self.IDs)
        if control_status == 'auto':
            if msg['e']['n'] == 'Temperature':
                tmp_value = msg['e']['value']
                self.temp_values.append(tmp_value)
            elif msg['e']['n'] == 'Soil_Moisture':
                mois_value = msg['e']['value']
                self.mois_values.append(mois_value)

            if len(self.temp_values) == len(self.mois_values) and len(self.mois_values) >1:
                self.ControlServo(self.temp_values, self.mois_values)

        elif control_status == 'manual':
            self.checkalarm(msg)
            self.manual_control()
            
    def manual_control(self):
        _schedul = self.my_req.get_manual_schedul(self.IDs)
        if _schedul["timers"] != []:
            for period in _schedul["timers"]:
                # print(period["days"])
                days = period["days"][1:] + [period["days"][0]]
                # print(days)
                weekday = [i for i in range(len(days)) if days[i] == 1]
                for i in weekday:
                    _time_now = datetime.datetime.now()
                    if i == _time_now.weekday():
                        _time_start = datetime.datetime.fromtimestamp(period["starttime"]/1000)
                        _time_stop = datetime.datetime.fromtimestamp(period["endtime"]/1000)
                        if _time_start.hour <= _time_now.hour <= _time_stop.hour:
                            if _time_start.minute <= _time_now.minute <= _time_stop.minute:
                                self.status = 'on'
                            else:
                                    self.status = 'off'
                        else:
                            self.status = 'off'

                        prev_status = self.my_req.get_status(self.IDs)

                        if self.status != prev_status:
                            self.my_req.put_status(self.IDs,self.status)
                            # print(f'------>>>> become {self.status} <<<<<--------')
                            self.sendActStatus(self.status)

    def ControlServo(self,temp_values, mois_values):
        if len(temp_values) > self.pre_times:
            temp_values.pop(0)
            mois_values.pop(0)
        mean_temp = sum(temp_values)/len(temp_values)
        mean_mois = sum(mois_values)/ len(mois_values)

        thresh = self.my_req.get_threshold(self.IDs)
        thresh['temp'], thresh['mois_min'], thresh['mois_max']
        # print(f'Temp Thresh:{thresh["temp"]}  Mois min Thresh:{thresh["mois_min"]} Mois max Thresh:{thresh["mois_max"]}')
        # print(f'mean Temp:{mean_temp}   mean Mois: {mean_mois}')

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
            # print(f'------>>>> become {self.status} <<<<<--------')
            self.sendActStatus(self.status)

    def sendActStatus(self, pump_state):
        topic = '/'.join([self.baseTopic, self.IDs['farm'],
                              self.IDs['section'], 'Devices', 'Pump_status'])
        # print(topic)
        __message = {
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

    def checkalarm(self, msg):
        if msg['e']['n'] == 'Soil_Moisture':
            thresh_min_mois = self.my_req.get_threshold(self.IDs)['mois_min']
            if msg['e']['value'] < thresh_min_mois:
                # print(f"alarm {msg['farmID']} {msg['sectionID']}")
                self.telegram_message['alert'] = 'The sensor of Soil Moisture is under the threshold'
                self.telegram_message['farm'] = msg['farmID']
                self.telegram_message['section'] = msg['sectionID']
                self.client.myPublish(self.alarm_topic, self.telegram_message)
                
if __name__ == "__main__":
    
    test = MoistController("hh")
    test.start()
    
    while True:
        time.sleep(1)
    