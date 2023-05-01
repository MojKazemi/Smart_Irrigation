import json
import cherrypy
from datetime import datetime
from cons_cal import consumption_calc as cons_cal
class catalogAPI:
    exposed = True

    def __init__(self):
        pass

    def GET(self,*uri,**params):
        
        if len(uri) >= 2 and uri[0] == 'catalog':
            with open('./catalog.json','r') as file:
                catalog = json.load(file)
            
            if uri[1] == 'broker_details':
                details = {}
                details['broker'] = catalog['broker']['address']
                details['port'] = catalog['broker']['port']
                details['baseTopic'] = catalog['baseTopic']
                return json.dumps(details)
            
            elif uri[1] == 'user_details':
                details = {}
                details['Users'] = catalog['Users']
                return json.dumps(details)

            elif uri[1] == 'farm_details':
                details = {}
                details['Farms'] = catalog['Farms']
                return json.dumps(details)
                
            elif uri[1] == 'pump_status': 
                farm,section = self.find_farm_sec(catalog,params)                      
                pump_status = catalog['Farms'][farm]['Sections'][section]["Devices"]["Pump"]["status"]
                
                return json.dumps(pump_status)

            elif uri[1] == 'threshold':
                thresh = {'temp':'','mois_min':'','mois_max':''}
                farm,section = self.find_farm_sec(catalog,params)                  
                vals = catalog['Farms'][farm]['Sections'][section]
                thresh['temp'] = vals["temp_threshold"]
                thresh['mois_min'] = vals["mois_min_threshold"]
                thresh['mois_max'] = vals["mois_max_threshold"]
                
                return json.dumps(thresh)
                        
            elif uri[1] == 'channelID':
                ch_ID = {}
                farm,section = self.find_farm_sec(catalog,params)                  
                vals = catalog['Farms'][farm]['Sections'][section]
                ch_ID['ch_ID'] = vals["TS_ChannelID"]
            
                return json.dumps(ch_ID)
                
            elif uri[1] == 'control_status':
                farm,section = self.find_farm_sec(catalog,params)                  
                vals = catalog['Farms'][farm]['Sections'][section]

                contorl_status = vals["control_status"]
            
                return json.dumps(contorl_status)
                            
            elif uri[1] == 'electrical_cost':
                return json.dumps(catalog['electrical_cost'])

            elif uri[1] == 'manual_schedul':
                farm, section = self.find_farm_sec(catalog, params)
                manual_schedul = catalog['Farms'][farm]['Sections'][section]['manual_schedul']
                
                return json.dumps(manual_schedul)

            elif uri[1] == 'telegram_setting':
                return json.dumps(catalog['telegram_setting'])

            elif uri[1] == 'all_topics':
                topics = []
                for user in catalog['Users'].values():
                    topics.append(user['topics'][params['type']])
                
                return json.dumps({"value":topics})

            elif uri[1] == 'sen_val':
                farm, sec = self.find_farm_sec(catalog, params)
                if params['type'] == 'Temperature':
                    sn_type = 'sensor1'
                elif params['type'] == 'Soil_Moisture':
                    sn_type = 'sensor2'
                else:
                    return json.dumps('The type of sensor is not valid')
                return json.dumps(str(catalog['Farms'][farm]['Sections'][sec]['Devices']['Sensors'][sn_type]['value']))
            


        elif uri[0] == 'statistic':
                        
            IDs = {
                'farmID': params['farmID'],
                'sectionID': params['sectionID']
                }
            
            with open('./catalog.json','r') as file:
                catalog = json.load(file)
            cost = catalog['electrical_cost'] 

            farm,section = self.find_farm_sec(catalog,params)                  
            vals = catalog['Farms'][farm]['Sections'][section]
            pump_power = vals['Devices']['Pump']['power']

            consumption = cons_cal('./pump_status.json',IDs, cost)

            if uri[1] == 'period':
                on_sec, power_cons = consumption.selective_time(start=params['start'],end=params['end'])
                
                return json.dumps(pump_power*power_cons)
            
            elif uri[1] == 'day':

                # Day should be present as %d/%m/%Y
                _, power_cons = consumption.daily_usage(day=params['day'])

                return json.dumps(round(pump_power * power_cons,2))

            elif uri[1] == 'month':
                # Month should be present as '01/2023'

                 _, power_cons = consumption.monthly_usage(month_year = params['month'])

                 return json.dumps(round(pump_power * power_cons,2))

            elif uri[1] == 'year':

                year_cost = consumption.yearly(params['year'])
                for key in year_cost:
                    year_cost[key] = round(year_cost[key] * pump_power,2)
                return json.dumps(year_cost)

        else:
            return 'Your request is not valid'

    def POST(self,*uri,**params):
        if uri[0] == "catalog":

            with open('./catalog.json') as file:
                catalog = json.load(file)
            
            if uri[1] == 'add_user':
                
                for _, val in catalog['Users'].items():
                    if params['new_user'] == val['userID']:
                        # raise cherrypy.HTTPError(500, "The username is taken. Try another")
                        msg = "The username has already taken. Try another"
                        return json.dumps(msg)
                        
                # user_key = 'user'+ str(len(catalog['Users'])+1)
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
                

            elif uri[1] == 'add_farm':
                user = self.check_user_pass(catalog, params)
                
                for _,val in catalog['Farms'].items():
                    if params['farmID'] == val['farmID']:
                        return json.dumps("The farm ID has already taken. Try another")

                # _key = 'farm' + str(len(catalog['Farms'])+1)
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

            elif uri[1] == 'add_section':
                user = self.check_user_pass(catalog, params)
                for key,val in catalog['Farms'].items():
                    if val["farmID"] == params['farmID']:
                        farm = key

                for key, val in catalog['Farms'][farm]['Sections'].items():
                    if params['new_section'] == val['sectionID']:
                        return json.dumps("The section name has already taken. Try another")
                        

                # _key = 'section' + str(len(catalog["Farms"][farm]["Sections"])+1)
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
                                "SensorType": "Temperature",
                                "value": None
                            },
                            "sensor2": {
                                "SensorID": 2,
                                "SensorName": "SEN-13322",
                                "SensorType": "Soil_Moisture",
                                "value": None
                            }
                        },
                        "Pump": {
                            "pumpID": 1,
                            "pumpName": "PMDC-12v-25w",
                            "power": 0.025,
                            "status": ""
                        }
                    }
                }
            

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                return json.dumps("The section has already added")
            
                

        if uri[0] == "statistics":

            with open('./pump_status.json') as file:
                    statis = json.load(file)

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            _root = f"{params['farmID']}/{params['sectionID']}"

            if uri[1] == "pump_status":
                statis["pump_status"].append({"t": str(timestamp),
                                            "r":_root ,
                                            "status": params['status']})
            
                jsonFile = open("pump_status.json", "w+")
                jsonFile.write(json.dumps(statis, indent=4))
                jsonFile.close()
        
    def PUT(self,*uri,**params):
        # Modify information
        try:
            if uri[0] == 'catalog':
                with open('./catalog.json','r') as file:
                    catalog = json.load(file)
                    
                farm, section = self.find_farm_sec(catalog, params)

                if uri[1] == 'pump_status':
                    if params['status'] == 'on' or params['status'] == 'off':
                        catalog['Farms'][farm]['Sections'][section]["Devices"]['Pump']['status'] = params['status']

                elif uri[1] == 'Temp_thresh':
                    if 0 < int(params['value']) < 100:
                        catalog['Farms'][farm]['Sections'][section]["temp_threshold"] = int(params['value'])

                elif uri[1] == 'Mois_min_thresh':
                    if 0 < int(params['value']) < 100:
                        catalog['Farms'][farm]['Sections'][section]["mois_min_threshold"] = int(params['value'])
                         
                elif uri[1] == 'Mois_max_thresh':
                    if 0 < int(params['value']) < 100:
                        catalog['Farms'][farm]['Sections'][section]["mois_max_threshold"] = int(params['value'])
                                                               
                elif uri[1] == 'control_status':
                    if params['value'] == 'auto' or params['value'] == 'manual':
                        catalog['Farms'][farm]['Sections'][section]["control_status"] = params['value']
                           
                elif uri[1]== 'manual_schedul':
                    catalog['Farms'][farm]['Sections'][section]["manual_schedul"] = json.loads(params["value"])

                elif uri[1] == 'sen_val':
                    farm, sec = self.find_farm_sec(catalog, params)
                    if params['type'] == 'Temperature':
                        sn_type = 'sensor1'
                    elif params['type'] == 'Soil_Moisture':
                        sn_type = 'sensor2'
                    else:
                        return json.dumps('The type of sensor is not valid')

                    catalog['Farms'][farm]['Sections'][sec]['Devices']['Sensors'][sn_type]['value'] = int(params['value'])
                    
                else:
                    raise cherrypy.HTTPError(500, "Please enter a valid request")
                #Now modify info in the catalog...

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                            
        except :
            raise cherrypy.HTTPError(500, "Please enter a valid request")
        
    def DELETE(self,*uri,**params):

        if uri[0] == "catalog":
            with open('./catalog.json') as file:
                catalog = json.load(file)

            with open('./catalog.json') as file:
                catalog = json.load(file)
            
            if uri[1] == 'delet_user':
                user = self.check_user_pass(catalog,params)

                del catalog['Users'][user]

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                return json.dumps("The user has already deleted")

            if uri[1] == 'delete_farm_of_user':
                user = self.check_user_pass(catalog, params)

                catalog['Users'][user]['farm_list'].remove(params['farmID'])

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                return json.dumps("The farm has already removed from the user")

            if uri[1] == 'delete_sec_of_farm':
                user = self.check_user_pass(catalog, params)
                farm, sec = self.find_farm_sec(catalog,params)

                del catalog['Farms'][farm]['Sections'][sec]

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                return json.dumps("The section has already removed from the farm")


            if uri[1] == 'delete_farm':
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
   
    def check_user_pass(self,catalog, params):
        for key, vals in catalog['Users'].items():
            if vals['userID'] == params['userID']:
                if vals['pass'] == params['pass']:
                    return key
                else:
                    return json.dumps("Password is not correct")
            
        return json.dumps("username is not correct")
        
    def find_farm_sec(self,catalog, params):
        try:
            for key, vals in catalog['Farms'].items():
                if vals['farmID'] == params['farmID']:
                    farm = key
            for key,vals in catalog['Farms'][farm]['Sections'].items():
                if vals['sectionID'] == params['sectionID']:
                    section = key
            # else:
            #     raise cherrypy.HTTPError(500, "user do not have access to the farm")
        except:
            raise cherrypy.HTTPError(500,"Please enter a valid request for parameters like: ?userID=Moj&farmID=Farm1&sectionID=Section1")
        return farm, section

if __name__ == '__main__':
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