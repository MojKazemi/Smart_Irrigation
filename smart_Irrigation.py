from threading import Thread
from catalog_API import catalogAPI
from bot import IrrigationBot
from sensors import Sensor
from controller import MoistController
import cherrypy
from MyMQTT_Reqs import MyMQTT, MyRequest
import time
import subprocess
import os
import json

class smart_Irrigation:
    def __init__(self):
        pass

    def start_node_red(self):
        os.system('node-red /data/flows.json')

    def start_webserver(self):
        conf={
            '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher()
            }
        }
        cherrypy.config.update({
            'server.socket_host': '127.0.0.1','server.socket_port':8080
        })
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        webapp = catalogAPI()
        cherrypy.tree.mount(webapp,'/',conf)
        cherrypy.engine.start()
        cherrypy.engine.block()

    def start_bot(self):
        my_req = MyRequest()
        broker, port,_ = my_req.get_broker()
        bot=IrrigationBot(broker, port)

        print("Bot started ...")
        while True:
            time.sleep(3)

    def start_sensors(self):
        my_req = MyRequest()
        broker, port, baseTopic = my_req.get_broker()
        catalog_user = my_req.get_catalog()
        catalog_farm = my_req.get_catalog_farm()

        Sensors = []

        for val_f in catalog_farm['Farms'].values():
            farmID = val_f['farmID']
            for val_s in val_f['Sections'].values():
                secID = val_s['sectionID']
                ch_ID = my_req.get_TS_chID(farmID,secID)
                for sen in val_s['Devices']['Sensors'].values():
                    senID = sen['SensorID']
                    SensorType = sen['SensorType']
                    sensor = Sensor(baseTopic,farmID,secID,senID,SensorType,broker,port,ch_ID)
                    Sensors.append(sensor)


        
        for sensor in Sensors:
            sensor.start()
        while True:
            for sensor in Sensors:
                sensor.sendData()
                time.sleep(5)

    def start_controller(self):
        test = MoistController("hh")
        test.start()
        
        while True:
            time.sleep(1)

    def start_all(self):
        t1 = Thread(target=self.start_webserver)
        t2 = Thread(target=self.start_bot)
        t3 = Thread(target=self.start_sensors)
        t4 = Thread(target=self.start_controller)
        # t5 = Thread(target=self.start_node_red)
        t1.start()
        time.sleep(2)
        t2.start()
        t3.start()
        t4.start()
        # t5.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        # t5.join()

if __name__ == '__main__':
    iot_device = smart_Irrigation()
    iot_device.start_all()