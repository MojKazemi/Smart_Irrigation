import json
import cherrypy

  
class Service_API(object):
    exposed = True

    def __init__(self):
        self.services = []

    def GET(self,*uri,**params):

        with open('./catalog.json','r') as file:
            catalog = json.load(file)

        if uri[0] == 'broker':
            details = {}
            details['broker'] = catalog['services']['mqtt_broker']['broker_address']
            details['port'] = catalog['services']['mqtt_broker']['broker_port']
            details['baseTopic'] = catalog['services']['mqtt_broker']['baseTopic']
            return json.dumps(details)
        
        elif uri[0] == 'statis_webserver':
            return json.dumps(catalog['services']['Statistic_webserver'])
        
        elif uri[0] == 'telegram_setting':
            return json.dumps(catalog['services']['telegram_setting'])
        
    def PUT(self,*uri,**params):
        '''
            /register_broker -->  params : address , port
            /register_baseTopic --> params : value
        '''

        with open('./catalog.json','r') as file:
            catalog = json.load(file)   
            
        if uri[0] == 'register_broker':
            catalog['services']['mqtt_broker']['broker_address'] = params['address']
            catalog['services']['mqtt_broker']['broker_port'] = int(params['port'])

        elif uri[0] == 'register_baseTopic':
            catalog['services']['mqtt_broker']['baseTopic'] = params['value']

        elif uri[0] == 'reg_statis_webserver':
            catalog['services']['Statistic_webserver']['st_address'] = params['address']
            catalog['services']['Statistic_webserver']['st_port'] = int(params['port'])

        else:
            raise cherrypy.HTTPError(500, "Please enter a valid request")

        jsonFile = open("catalog.json", "w+")
        jsonFile.write(json.dumps(catalog, indent=4))
        jsonFile.close()

        return json.dumps('Services have updated')
    