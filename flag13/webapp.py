import os, os.path
import random
import cherrypy
import csv


class User:
    def __init__(self,user,password):
        self.user = user
        self.password = password
        self.token = hash((self,  random.randint(0,1024)))


    def validate(self,usr,pwd):
        return self.user == usr and self.password == pwd


    content = "";


def readFile(path):
    f=open(path, "r")
    contents =f.read()
    return contents

users = []

with open('users.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=':')
    for row in csv_reader:
        users.append(User(row[0],row[1]))


class Flag13:




    @cherrypy.expose
    def index(self,**args):
        if 'token' in cherrypy.session.keys():
            user = self.findUser()
            replace = 'Try to log in as admin'
            if 'admin' in args.keys() and args['admin'].lower()== 'true':
                print('admin' in args.keys() and args['admin'])
                print(args['admin'])
                replace = readFile("flag.txt")
            return readFile("static/page.html").replace("CONTENT",replace)
        return readFile("static/index.html")


    @cherrypy.expose
    def login(self,user,password):
        for u in users:
            if u.user == user and u.password == password:
                cherrypy.session['token'] = u.token
                raise cherrypy.HTTPRedirect('/?admin=false')
                # return "logged"
        raise cherrypy.HTTPRedirect('/')



    @cherrypy.expose
    def logout(self):
        del cherrypy.session['token']
        raise cherrypy.HTTPRedirect('/')


    def findUser(self):
        token = cherrypy.session['token'];

        for u in users:
            if u.token == token:
                return u;
        del cherrypy.session['token']
        raise cherrypy.HTTPRedirect('/')





if __name__ == '__main__':



    conf = {
        '/res':
            {'tools.staticdir.on': True,
             'tools.staticdir.dir':  "./static/res"
             },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            # 'tools.auth_basic.checkpassword': validate_password,

        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(Flag13(), '/', conf)


