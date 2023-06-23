
import json
import random
import time, datetime
import requests

from MyMQTT_Reqs import MyMQTT


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

    with open('./sensors_conf.json', 'r') as file:
        se_conf = json.load(file)

    broker_add = se_conf["broker_address"]
    broker_port = se_conf["broker_port"]
    bese_topic = se_conf["base_topic"]

    rc_add = se_conf["rc_address"]
    rc_port = se_conf["rc_port"]

    # broker_conf = requests.get(f'http://{rc_add}:{rc_port}/services/broker').json()
    
    # if broker_conf['broker'] != broker_add or broker_conf['port'] != broker_port:
    requests.put(f'http://{rc_add}:{rc_port}/services/register_broker?address={broker_add}&port={broker_port}')

    # if broker_conf['baseTopic'] != bese_topic:
    requests.put(f'http://{rc_add}:{rc_port}/services/register_baseTopic?value={bese_topic}')
    
    catalog_user = requests.get(f'http://{rc_add}:{rc_port}/catalog/user_details').json()
    catalog_farm = requests.get(f'http://{rc_add}:{rc_port}/catalog/farm_details').json()

    Sensors = []

    for val_f in catalog_farm['Farms'].values():
        farmID = val_f['farmID']
        for val_s in val_f['Sections'].values():
            secID = val_s['sectionID']
            for sen in val_s['Devices']['Sensors'].values():
                senID = sen['SensorID']
                SensorType = sen['SensorType']

                sensor = Sensor(
                    bese_topic,
                    farmID,secID,senID,SensorType,
                    broker_add,
                    broker_port
                )
                Sensors.append(sensor)


    
    for sensor in Sensors:
        sensor.start()
    while True:
        for sensor in Sensors:
            sensor.sendData()
            # print(sensor.farmID,sensor.secID, sensor.ts_chID)
            time.sleep(5)
