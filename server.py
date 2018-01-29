import cherrypy
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import re


# cherrypy.config.update({'server.socket_port': 3000})
# cherrypy.engine.restart()

# mongodb://alpit_anand:DBADBADBA1@ds119028.mlab.com:19028/collect
# mongodb://localhost:27017 when using locally
data = []
client = MongoClient(' mongodb://alpit_anand:DBADBADBA1@ds119028.mlab.com:19028/collect')
db = client.collect
collection = db.stock_data
cursor = collection.find({}).sort("CLOSE", -1)
c_dir = os.path.dirname(__file__)
count = 0
while count < 10:
    print(cursor[count])
    data.append(cursor[count])
    count = count + 1


class Dbextractor(object):

    @cherrypy.expose
    def index(self):
        env = Environment(
            loader=FileSystemLoader(os.path.join(c_dir, 'templates')),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template = env.get_template('mytemplate.html')
        return template.render(data=data)

    @cherrypy.expose
    def search(self, sc_name=None):
        env = Environment(
            loader=FileSystemLoader(os.path.join(c_dir, 'templates')),
            autoescape=select_autoescape(['html', 'xml'])
        )
        print(sc_name)
        regx = re.compile(sc_name, re.IGNORECASE)
        find = collection.find_one({"SC_NAME": regx})
        if find:
            template = env.get_template('search.html')
            return template.render(searched_data=find)
        else:
            template = env.get_template('not_found.html')
            return template.render()

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './templates/static'
        }

    }
    webapp = Dbextractor()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', })
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')), })
    cherrypy.quickstart(webapp, '/', conf)
