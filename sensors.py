
import json
import random
import time, datetime
import requests

from MyMQTT_Reqs import MyMQTT, MyRequest


class Sensor:
    """docstring for Sensor"""     #baseTopic,userID,farmID,secID,senID

    def __init__(self, baseTopic, farmID, secID, senID ,SensorType, broker, port):
        self.baseTopic = baseTopic
        self.farmID, self.secID = farmID, secID
        self.sensorID = str(senID)
        self.topic = '/'.join([self.baseTopic,'data' ,self.farmID, self.secID, self.sensorID])
        self.client = MyMQTT(self.sensorID, broker, port, None)
        sensorunit = {'Temperature':'C', 'Soil_Moisture':'%'}
        self.__message = {
            'farmID': self.farmID,
            'sectionID': self.secID,
            'bn': self.sensorID,
            'e': [{'n': SensorType, 'value': '', 'timestamp': '', 'unit': sensorunit[SensorType]}]
        }

    def sendData(self):
        message = self.__message
        if self.__message['e'][0]['n'] == 'Temperature':
            sensor_value = random.randint(10, 30)
        else:
            sensor_value = random.randint(0, 100)
        # General Broker
        message['e'][0]['value'] = sensor_value
        message['e'][0]['timestamp'] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.client.myPublish(self.topic, message)


    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

if __name__ == '__main__':
    my_req = MyRequest()
    broker, port, baseTopic = my_req.get_broker()
    catalog_user = my_req.get_catalog()
    catalog_farm = my_req.get_catalog_farm()

    Sensors = []

    for val_f in catalog_farm['Farms'].values():
        farmID = val_f['farmID']
        for val_s in val_f['Sections'].values():
            secID = val_s['sectionID']
            for sen in val_s['Devices']['Sensors'].values():
                senID = sen['SensorID']
                SensorType = sen['SensorType']
                sensor = Sensor(baseTopic,farmID,secID,senID,SensorType,broker,port)#,ch_ID)
                Sensors.append(sensor)


    
    for sensor in Sensors:
        sensor.start()
    while True:
        for sensor in Sensors:
            sensor.sendData()
            # print(sensor.farmID,sensor.secID, sensor.ts_chID)
            time.sleep(5)
