
import json
import random
import time, datetime
import requests

from MyMQTT_Reqs import MyMQTT, MyRequest, ts_publish


class Sensor:
    """docstring for Sensor"""     #baseTopic,userID,farmID,secID,senID

    def __init__(self, baseTopic, userID, farmID, secID, senID ,SensorType, broker, port, TS_channelID=''):
        self.baseTopic = baseTopic
        self.userID,  self.farmID, self.secID = userID, farmID, secID
        self.sensorID = str(senID)
        self.topic = '/'.join([self.baseTopic, self.userID, self.farmID,
                              self.secID, self.sensorID])
        self.client = MyMQTT(self.sensorID, broker, port, None)
        sensorunit = {'Temperature':'C', 'Soil_Moisture':'%'}
        self.__message = {
            'userID': self.userID,
            'farmID': self.farmID,
            'sectionID': self.secID,
            'bn': self.sensorID,
            'e': {'n': SensorType, 'value': '', 'timestamp': '', 'unit': sensorunit[SensorType]}
        }
        self.ts_chID = TS_channelID
        self.publish_TS = ts_publish(self.ts_chID, ts_conf='ts_conf.json')

    def sendData(self):
        message = self.__message
        if self.__message['e']['n'] == 'Temperature':
            sensor_value = random.randint(10, 30)
            TS_field = 'field1'
        else:
            sensor_value = random.randint(0, 100)
            TS_field = 'field2'
        # General Broker
        message['e']['value'] = sensor_value
        message['e']['timestamp'] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.client.myPublish(self.topic, message)

        # Thingspeak Broker
        payload = f"&{TS_field}=" + str(sensor_value)
        print(payload)
        self.publish_TS.tsPublish(payload)

    def start(self):
        self.client.start()
        self.publish_TS.start()

    def stop(self):
        self.client.stop()

if __name__ == '__main__':
    my_req = MyRequest()
    broker, port, baseTopic = my_req.get_broker()
    catalog_user = my_req.get_catalog()

    Sensors = []
    for val in catalog_user['Users'].values():
        userID = val['userID']
        for val_f in val['Farms'].values():
            farmID = val_f['farmID']
            for val_s in val_f['Sections'].values():
                secID = val_s['sectionID']
                ch_ID = my_req.get_TS_chID(userID,farmID,secID)
                for sen in val_s['Devices']['Sensors'].values():
                    senID = sen['SensorID']
                    SensorType = sen['SensorType']
                    sensor = Sensor(baseTopic,userID,farmID,secID,senID,SensorType,broker,port,ch_ID)
                    Sensors.append(sensor)


    
    for sensor in Sensors:
        sensor.start()
    while True:
        for sensor in Sensors:
            sensor.sendData()
            print(sensor.userID,sensor.farmID,sensor.secID, sensor.ts_chID)
            time.sleep(5)
