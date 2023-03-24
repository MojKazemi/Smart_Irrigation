import json
import cherrypy

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
                
            elif uri[1] == 'pump_status':
                try:
                    for key,vals in catalog['Users'].items():
                        if vals['userID'] == params['userID']:
                            user = key
                            
                    for key, vals in catalog['Users'][user]['Farms'].items():
                        if vals['farmID'] == params['farmID']:
                            farm = key                            
                    
                    for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                        if vals['sectionID'] == params['sectionID']:
                            pump_status = vals["Devices"]["Pump"]["status"]
                
                    return json.dumps(pump_status)
                    
                except:
                    raise cherrypy.HTTPError(500,"Please enter a valid request")


            elif uri[1] == 'threshold':
                thresh = {'temp':'','mois_min':'','mois_max':''}
                # if len(params) == 3:
                try:
                    for key,vals in catalog['Users'].items():
                        if vals['userID'] == params['userID']:
                            user = key
                            
                    for key, vals in catalog['Users'][user]['Farms'].items():
                        if vals['farmID'] == params['farmID']:
                            farm = key                            
                    
                    for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                        if vals['sectionID'] == params['sectionID']:
                            thresh['temp'] = vals["temp_threshold"]
                            thresh['mois_min'] = vals["mois_min_threshold"]
                            thresh['mois_max'] = vals["mois_max_threshold"]
                
                    return json.dumps(thresh)
                except :
                        raise cherrypy.HTTPError(500,"Please enter a valid request for ex.: /catalog/threshold?userID=Moj&farmID=Farm1&sectionID=Section1")
                # else:
                    # return 'Insert userID, FarmID, and sectionID for ex.: /catalog/threshold?userID=user1&farmID=farm1&sectionID=section1'
            
            elif uri[1] == 'channelID':
                ch_ID = {}
                try:
                    for key,vals in catalog['Users'].items():
                        if vals['userID'] == params['userID']:
                            user = key
                            
                    for key, vals in catalog['Users'][user]['Farms'].items():
                        if vals['farmID'] == params['farmID']:
                            farm = key                            
                    
                    for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                        if vals['sectionID'] == params['sectionID']:
                            ch_ID['ch_ID'] = vals["TS_ChannelID"]
                
                    return json.dumps(ch_ID)
                
                except :
                        raise cherrypy.HTTPError(500,"Please enter a valid request for ex.: /catalog/threshold?userID=Moj&farmID=Farm1&sectionID=Section1")

        else:
            return 'Your request is not valid'

    def POST(self):
        pass

    def PUT(self,*uri,**params):
        # Modify information
        try:
            if uri[0] == 'catalog':
                with open('./catalog.json','r') as file:
                    catalog = json.load(file)
                
                if uri[1] == 'pump_status':
                    if params['status'] == 'on' or params['status'] == 'off':

                        for key,vals in catalog['Users'].items():
                            if vals['userID'] == params['userID']:
                                user = key
                                
                        for key, vals in catalog['Users'][user]['Farms'].items():
                            if vals['farmID'] == params['farmID']:
                                farm = key                            
                        
                        for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                            if vals['sectionID'] == params['sectionID']:
                                vals["Devices"]['Pump']['status'] = params['status']

                elif uri[1] == 'Temp_thresh':
                    if 0 < int(params['value']) < 100:
                        for key,vals in catalog['Users'].items():
                            if vals['userID'] == params['userID']:
                                user = key
                            
                        for key, vals in catalog['Users'][user]['Farms'].items():
                            if vals['farmID'] == params['farmID']:
                                farm = key                            
                    
                        for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                            if vals['sectionID'] == params['sectionID']:
                                vals["temp_threshold"] = int(params['value'])
                elif uri[1] == 'Mois_min_thresh':
                    if 0 < int(params['value']) < 100:
                        for key,vals in catalog['Users'].items():
                            if vals['userID'] == params['userID']:
                                user = key
                            
                        for key, vals in catalog['Users'][user]['Farms'].items():
                            if vals['farmID'] == params['farmID']:
                                farm = key                            
                    
                        for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                            if vals['sectionID'] == params['sectionID']:
                                vals["mois_min_threshold"] = int(params['value'])

                elif uri[1] == 'Mois_max_thresh':
                    if 0 < int(params['value']) < 100:
                        for key,vals in catalog['Users'].items():
                            if vals['userID'] == params['userID']:
                                user = key
                            
                        for key, vals in catalog['Users'][user]['Farms'].items():
                            if vals['farmID'] == params['farmID']:
                                farm = key                            
                    
                        for key,vals in catalog['Users'][user]['Farms'][farm]['Sections'].items():
                            if vals['sectionID'] == params['sectionID']:
                                vals["mois_max_threshold"] = int(params['value'])
                else:
                    raise cherrypy.HTTPError(500, "Please enter a valid request")
                #Now modify info in the catalog...

                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                            
        except :
            raise cherrypy.HTTPError(500, "Please enter a valid request")
        

    def DELETE(self):
        pass


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