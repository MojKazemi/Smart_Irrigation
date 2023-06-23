import cherrypy
import json


class Select_UserFarmSec():
    def __init__(self, catalog, params):
        self.catalog = catalog
        self.params = params
    
    # by this Function, User's password will be checked
    def check_user_pass(self):
        for key, vals in self.catalog['Users'].items():
            if vals['userID'] == self.params['userID']:
                if vals['pass'] == self.params['pass']:
                    return key
                else:
                    return json.dumps("Password is not correct")
            
        return json.dumps("username is not correct")
        
    def find_farm_sec(self):
        try:
            for key, vals in self.catalog['Farms'].items():
                if vals['farmID'] == self.params['farmID']:
                    farm = key
            for key,vals in self.catalog['Farms'][farm]['Sections'].items():
                if vals['sectionID'] == self.params['sectionID']:
                    section = key
            # else:
            #     raise cherrypy.HTTPError(500, "user do not have access to the farm")
        except:
            raise cherrypy.HTTPError(500,"Please enter a valid request for parameters like: ?userID=Moj&farmID=Farm1&sectionID=Section1")
        return farm, section
