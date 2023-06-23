import cherrypy
import json
from datetime import datetime
from Statis_Data.cons_cal import consumption_calc as cons_cal
import requests
# from catalog_API import Select_UserFarmSec


class Select_FarmSec():
    def __init__(self, Farms_details, params):
        self.Farms_details = Farms_details
        self.params = params
    
       
    def find_farm_sec(self):
        try:
            for key, vals in self.Farms_details['Farms'].items():
                if vals['farmID'] == self.params['farmID']:
                    farm = key
            for key,vals in self.Farms_details['Farms'][farm]['Sections'].items():
                if vals['sectionID'] == self.params['sectionID']:
                    section = key
        except:
            raise cherrypy.HTTPError(500,"Please enter a valid request for parameters like: ?farmID=Farm1&sectionID=Section1")
        return farm, section

class EnergyCons(object):

    exposed = True
    def __init__(self, conf_file = './Statis_Data/EnCons_conf.json', DB_status='./Statis_Data/pump_status.json'):
        with open(conf_file, 'r') as file:
            rc_conf = json.load(file)
        self.rc_add = rc_conf['rc_address']
        self.rc_port = rc_conf['rc_port']
        self.DB_status = DB_status
        self.IDs = {
            'farmID': '',
            'sectionID': ''
            }
        requests.put(f'http://{self.rc_add}:{self.rc_port}/services/reg_statis_webserver?address={rc_conf["Server_soket_host"]}&port={rc_conf["Server_soket_port"]}')


    def GET(self,*uri,**params):
                        
        self.IDs['farmID'] = params['farmID']
        self.IDs['sectionID'] = params['sectionID']
            
        
        cost = requests.get(f'http://{self.rc_add}:{self.rc_port}/catalog/electrical_cost').json()
        Farms_details = requests.get(f'http://{self.rc_add}:{self.rc_port}/catalog/farm_details').json() 

        S_UserFarmSec = Select_FarmSec(Farms_details, params)
        farm,section = S_UserFarmSec.find_farm_sec()

        vals = Farms_details['Farms'][farm]['Sections'][section]
        pump_power = vals['Devices']['Pump']['power']

        consumption = cons_cal(self.DB_status, self.IDs, cost)

        if uri[0] == 'period':
            on_sec, power_cons = consumption.selective_time(start=params['start'],end=params['end'])
            
            return json.dumps(pump_power*power_cons)
        
        elif uri[0] == 'day':

            # Day should be present as %d/%m/%Y
            _, power_cons = consumption.daily_usage(day=params['day'])

            return json.dumps(round(pump_power * power_cons,2))

        elif uri[0] == 'month':
            # Month should be present as '01/2023'

                _, power_cons = consumption.monthly_usage(month_year = params['month'])

                return json.dumps(round(pump_power * power_cons,2))

        elif uri[0] == 'year':
            year_cost = consumption.yearly(params['year'])
            for key in year_cost:
                year_cost[key] = round(year_cost[key] * pump_power,2)
            return json.dumps(year_cost)

        else:
            raise cherrypy.HTTPError(500, "Please enter a valid request")
        
    def POST(self,*uri,**params):
        # if uri[0] == "statistics":

        with open(self.DB_status) as file:
            statis = json.load(file)

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        _root = f"{params['farmID']}/{params['sectionID']}"

        # if uri[0] == "pump_status":
        statis["pump_status"].append({"t": str(timestamp),
                                    "r":_root ,
                                    "status": params['status']})
    
        jsonFile = open(self.DB_status, "w+")
        jsonFile.write(json.dumps(statis, indent=4))
        jsonFile.close()
        return json.dumps('Posted new event')
            

if __name__ == "__main__":

    conf_file='./Statis_Data/EnCons_conf.json'
    with open(conf_file, 'r')as file:
        config = json.load(file)
    Server_soket_host = config['Server_soket_host']
    Server_soket_port = config['Server_soket_port']

    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    EnergyConsumption = EnergyCons(conf_file, DB_status='./Statis_Data/pump_status.json')
    cherrypy.tree.mount(EnergyConsumption,'/statistic',conf)

    cherrypy.config.update({'server.socket_host': Server_soket_host})
    cherrypy.config.update({'server.socket_port': Server_soket_port})

    cherrypy.engine.start()
    cherrypy.engine.block()