
import os, os.path
import random
import cherrypy
import csv
import sqlite3
from sqlite3 import Error
import hashlib
import base64
import binascii
import time


class DbHelper:
    def __init__(self,dbfile):
        self.dbfile=dbfile


    def select(self,query,params):
        conn = sqlite3.connect(self.dbfile)
        cur = conn.cursor()
        if type(params) is tuple:
            cur.execute(query, params)
        else:
            cur.execute(query,(params,))
        return cur.fetchall()

    def update(self,query,params):
        conn = sqlite3.connect(self.dbfile)
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password



def readFile(path):
    f = open(path, "r")
    contents = f.read()
    return contents




class CoreSystem:

    def __init__(self):
        self.dbhelper = DbHelper('database.db')



    def getFlagString(self,token,userid):
        print(type(userid))
        flags = self.dbhelper.select("select chalenge from tblflags  where id not in (select id from tblflags  join tblflagsusers on id = flagid and userid =?)",userid)
        value = ""
        for flag in flags:
            value = value + '<option>'+flag[0]+'</option>'
        return value



    @cherrypy.expose
    def index(self):
        if 'token' in cherrypy.session.keys():
            return readFile("static/page.html").replace("FLAGIDS",self.getFlagString(cherrypy.session['token'],cherrypy.session['userid'])) #
        return readFile("static/index.html")

    @cherrypy.expose
    def login(self, user, password):
        user = self.dbhelper.select("select id,uname,passwd from tblusers where uname =? ", user)
        if user is not None and len(user)>0:
             if verify_password(user[0][2],password):
                token = base64.b64encode(hashlib.sha256(str(random.randint(0, 1024)).encode("ascii")).digest()).decode('ascii')
                cherrypy.session['token'] = token
                cherrypy.session['userid'] = user[0][0]
                # return "logged"

        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def submit(self,flagname='',flagvalue=''):
        if 'userid' not in cherrypy.session.keys():
            raise cherrypy.HTTPRedirect('/?msg=1')

        result = self.dbhelper.select("select id from tblflags where chalenge=? and flag=?",(flagname,flagvalue) )
        if (len(result)==0):
            raise cherrypy.HTTPRedirect('/?msg=2')
        flagid = result[0][0]
        userid = int(cherrypy.session['userid'])
        timestamp = int(time.time())
        self.dbhelper.update("insert into tblflagsusers values (?,?,?)",(flagid,userid,timestamp))



        raise cherrypy.HTTPRedirect('/?msg=0')

    @cherrypy.expose
    def logout(self):
        del cherrypy.session['token']
        raise cherrypy.HTTPRedirect('/')



    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def data(self, pagenumber=0, search=""):
    #
    #     try:
    #         conn = sqlite3.connect("database.db")
    #         cur = conn.cursor()
    #         search = search.upper()
    #
    #         query = "SELECT * FROM tblusers where (fname like '%" + search + "%') or (sname  like '%" + search + "%') LIMIT " + str(pagenumber) +",10";
    #         print(query)
    #         cur.execute( query )
    #         rows = cur.fetchall()
    #         result = []
    #         for row in rows:
    #            result.append( {
    #               'id' : str(row[0]),
    #               'fname': row[1],
    #               'sname': row[2],
    #               'credits': row[3]
    #             })
    #         return result
    #     except Error as e:
    #         print (e)
    #         return str(e)
    #     finally:
    #         conn.close()




if __name__ == '__main__':
    conf = {


        '/res':
            {'tools.staticdir.on': True,
             'tools.staticdir.dir': "./static/res"
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
    cherrypy.quickstart(CoreSystem(), '/', conf)












