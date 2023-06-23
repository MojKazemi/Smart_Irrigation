import cherrypy
from APIs.Catalog_API import catalogAPI
from APIs.Service_API import Service_API

class web_server:
    def __init__(self,WebServer_host,WebServer_port):
        self.WebServer_host = WebServer_host
        self.WebServer_port = WebServer_port
        self.conf={
            '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
            }
        }
    
    def start(self):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.tree.mount(catalogAPI(),'/catalog',self.conf)
        cherrypy.tree.mount(Service_API(),'/services',self.conf)

        cherrypy.config.update({'server.socket_host': '127.0.0.1'})
        cherrypy.config.update({'server.socket_port': 8080})

        cherrypy.engine.start()
        cherrypy.engine.block()

if __name__ == '__main__':
    Irrig_server = web_server('127.0.0.1',8080)
    Irrig_server.start()