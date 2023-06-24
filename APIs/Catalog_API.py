import cherrypy
import json
from APIs.Select_UFS import Select_UserFarmSec

class catalogAPI(object):
    exposed = True

    def __init__(self):
       pass
    

    def GET(self,*uri,**params):
        
        # by this Get function we take data from Catalog.json.
        # if len(uri) >= 2 and uri[0] == 'catalog':
        
        with open('./catalog.json','r') as file:
            catalog = json.load(file)
        S_UserFarmSec = Select_UserFarmSec(catalog, params)

        # if uri[0] == 'broker_details':
        #     details = {}
        #     details['broker'] = catalog['broker']['address']
        #     details['port'] = catalog['broker']['port']
        #     details['baseTopic'] = catalog['baseTopic']
        #     return json.dumps(details)
        
        if uri[0] == 'user_details':
            details = {}
            details['Users'] = catalog['Users']
            return json.dumps(details)

        elif uri[0] == 'farm_details':
            details = {}
            details['Farms'] = catalog['Farms']
            return json.dumps(details)
            
        elif uri[0] == 'pump_status': 
            farm,section = S_UserFarmSec.find_farm_sec()                      
            pump_status = catalog['Farms'][farm]['Sections'][section]["Devices"]["Pump"]["status"]
            
            return json.dumps(pump_status)

        elif uri[0] == 'threshold':
            thresh = {'temp':'','mois_min':'','mois_max':''}
            farm,section = S_UserFarmSec.find_farm_sec()                  
            vals = catalog['Farms'][farm]['Sections'][section]
            thresh['temp'] = vals["temp_threshold"]
            thresh['mois_min'] = vals["mois_min_threshold"]
            thresh['mois_max'] = vals["mois_max_threshold"]
            
            return json.dumps(thresh)
                    
        elif uri[0] == 'channelID':
            ch_ID = {}
            farm,section = S_UserFarmSec.find_farm_sec()                  
            vals = catalog['Farms'][farm]['Sections'][section]
            ch_ID['ch_ID'] = vals["TS_ChannelID"]
        
            return json.dumps(ch_ID)
            
        elif uri[0] == 'control_status':
            farm,section = S_UserFarmSec.find_farm_sec()                  
            vals = catalog['Farms'][farm]['Sections'][section]

            contorl_status = vals["control_status"]
        
            return json.dumps(contorl_status)
                        
        elif uri[0] == 'electrical_cost':
            return json.dumps(catalog['electrical_cost'])

        elif uri[0] == 'manual_schedul':
            farm, section = S_UserFarmSec.find_farm_sec()
            manual_schedul = catalog['Farms'][farm]['Sections'][section]['manual_schedul']
            
            return json.dumps(manual_schedul)

        elif uri[0] == 'sen_val':
            farm, sec = S_UserFarmSec.find_farm_sec()
            if params['type'] == 'Temperature':
                sn_type = 'sensor1'
            elif params['type'] == 'Soil_Moisture':
                sn_type = 'sensor2'
            else:
                return json.dumps('The type of sensor is not valid')
            return json.dumps(str(catalog['Farms'][farm]['Sections'][sec]['Devices']['Sensors'][sn_type]['value']))
            
        
    def POST(self,*uri,**params):
            
        # By this function, data about users and ... will be Created in Catalog.json
        with open('./catalog.json') as file:
            catalog = json.load(file)

        S_UserFarmSec = Select_UserFarmSec(catalog, params)

        if uri[0] == 'add_user':
            
            for _, val in catalog['Users'].items():
                if params['new_user'] == val['userID']:
                    
                    msg = "The username has already taken. Try another"
                    return json.dumps(msg)
                    
            
            catalog['Users'][params['new_user']]={
                "userID":params['new_user'],
                "pass":params['pass'],
                "farm_list" : []
            }
            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            msg = "The user has already added"
            return json.dumps(msg)
            

        elif uri[0] == 'add_farm':
            user = S_UserFarmSec.check_user_pass()
            
            for _,val in catalog['Farms'].items():
                if params['farmID'] == val['farmID']:
                    return json.dumps("The farm ID has already taken. Try another")

            
            catalog['Farms'][params['farmID']]={
                "farmID": params['farmID'],
                "Sections": {}
            }
            catalog["Users"][user]["farm_list"].append(params['farmID'])

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            msg = "The farm has already added"
            return json.dumps(msg)

        elif uri[0] == 'add_section':
            user = S_UserFarmSec.check_user_pass()
            for key,val in catalog['Farms'].items():
                if val["farmID"] == params['farmID']:
                    farm = key

            for key, val in catalog['Farms'][farm]['Sections'].items():
                if params['new_section'] == val['sectionID']:
                    return json.dumps("The section name has already taken. Try another")
                    

            catalog["Farms"][farm]["Sections"][params['new_section']] = {
                "sectionID":params['new_section'],
                "control_status": "",
                "temp_threshold": None,
                "mois_min_threshold": None,
                "mois_max_threshold": None,
                "Devices":{

                    "Sensors": {
                        "sensor1": {
                            "SensorID": 1,
                            "SensorName": "DHT11",
                            "SensorType": "Temperature"
                        },
                        "sensor2": {
                            "SensorID": 2,
                            "SensorName": "SEN-13322",
                            "SensorType": "Soil_Moisture"
                        }
                    },
                    "Pump": {
                        "pumpID": 1,
                        "pumpName": "PMDC-12v-25w",
                        "power": 0.025
                    }
                }
            }
        

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            return json.dumps("The section has already added")      
        
    def PUT(self,*uri,**params):
        # Modify information
        #In this function we can Update data about users, farms and ... will be updated.
        try:
            with open('./catalog.json','r') as file:
                catalog = json.load(file)

            S_UserFarmSec = Select_UserFarmSec(catalog, params)                
            farm, section = S_UserFarmSec.find_farm_sec()

            if uri[0] == 'pump_status':
                if params['status'] == 'on' or params['status'] == 'off':
                    catalog['Farms'][farm]['Sections'][section]["Devices"]['Pump']['status'] = params['status']

            elif uri[0] == 'Temp_thresh':
                if 0 < int(params['value']) < 100:
                    catalog['Farms'][farm]['Sections'][section]["temp_threshold"] = int(params['value'])

            elif uri[0] == 'Mois_min_thresh':
                if 0 < int(params['value']) < 100:
                    catalog['Farms'][farm]['Sections'][section]["mois_min_threshold"] = int(params['value'])
                        
            elif uri[0] == 'Mois_max_thresh':
                if 0 < int(params['value']) < 100:
                    catalog['Farms'][farm]['Sections'][section]["mois_max_threshold"] = int(params['value'])
                                                            
            elif uri[0] == 'control_status':
                if params['value'] == 'auto' or params['value'] == 'manual':
                    catalog['Farms'][farm]['Sections'][section]["control_status"] = params['value']
                        
            elif uri[0]== 'manual_schedul':
                catalog['Farms'][farm]['Sections'][section]["manual_schedul"] = json.loads(params["value"])

            elif uri[0] == 'sen_val':
                # farm, sec = S_UserFarmSec.find_farm_sec(catalog, params)
                if params['type'] == 'Temperature':
                    sn_type = 'sensor1'
                elif params['type'] == 'Soil_Moisture':
                    sn_type = 'sensor2'
                else:
                    return json.dumps('The type of sensor is not valid')

                catalog['Farms'][farm]['Sections'][section]['Devices']['Sensors'][sn_type]['value'] = int(params['value'])
                
            else:
                raise cherrypy.HTTPError(500, "Please enter a valid request")
            #Now modify info in the catalog...

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            
                            
        except :
            raise cherrypy.HTTPError(500, "Please enter a valid request")
        
    def DELETE(self,*uri,**params):

        # In this function data about users, farms and ... will be Deleted.
        # if uri[0] == "catalog":
        with open('./catalog.json') as file:
            catalog = json.load(file)

        S_UserFarmSec = Select_UserFarmSec(catalog, params)          
        if uri[0] == 'delet_user':
            user = S_UserFarmSec.check_user_pass(catalog,params)

            del catalog['Users'][user]

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            return json.dumps("The user has already deleted")

        if uri[0] == 'delete_farm_of_user':
            user = S_UserFarmSec.check_user_pass(catalog, params)

            catalog['Users'][user]['farm_list'].remove(params['farmID'])

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            return json.dumps("The farm has already removed from the user")

        if uri[0] == 'delete_sec_of_farm':
            user = S_UserFarmSec.check_user_pass(catalog, params)
            farm, sec = self.find_farm_sec(catalog,params)

            del catalog['Farms'][farm]['Sections'][sec]

            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()
            return json.dumps("The section has already removed from the farm")


        if uri[0] == 'delete_farm':
            if params['userID'] == catalog['user_admin']:
                if params['pass'] == catalog['admin_pass']:
                    for key, vals in catalog['Farms'].items():
                        if vals['farmID'] == params['farmID']:
                            farm = key

                            del catalog["Farms"][farm]

                            jsonFile = open("catalog.json", "w+")
                            jsonFile.write(json.dumps(catalog, indent=4))
                            jsonFile.close()
                            return json.dumps("The farm has already deleted")
                return json.dumps("The admin's password is incorrect")
            return json.dumps("The user of admin is incorrect")
   
