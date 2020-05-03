#!/usr/bin/python3
"""Class to check if a URL is live or not
Caches results in sqlite3 database to speed up processing.
By Joseph T. Foley <foley AT RU.IS>  
Created 2020-05-02
MIT License
"""
import argparse
#import requests
import datetime
#from urllib.parse import urlparse,urlunparse
import sqlite3
import checklink

class checklinkdb(checklink.checklink):
    """we want most of checklink, but we will add DB functionality"""
    def __init__(self, timeout=None):
        """setup"""
        super().__init__(timeout)
        self.conn = sqlite3.connect("checklink.db")
        # "PRIMARY KEY" later
        self.conn.execute('''CREATE TABLE IF NOT EXISTS linkinfo (url UNIQUE ON CONFLICT REPLACE , status INT, updated DATE) ''')
        ## We'll use 0 for dead, 1 for live
        self.conn.commit()

        
    def updatelinkinfo(self, link, status):
        """Dump info in DB"""        
        today = str(datetime.date.today())
        alive = 0
        if status:
            alive = 1
        sqlcmd = "INSERT INTO linkinfo (url,status,updated) VALUES (?,?,?)"
        values = (link,alive,today)
        print(sqlcmd, values)
        self.conn.execute(sqlcmd, (link,alive,today))
        self.conn.commit()

    def getlinkstatus(self, link):
        """See if we have link informatin in the database
        True if live,
        False if dead,
        None if not in DB"""        
        sqlcmd = "SELECT status from linkinfo WHERE url=?"
        c = self.conn.execute(sqlcmd, (link,))
        val = c.fetchone()
        if val is not None:
            if int(val[0]) > 0:
                return(True)
            else:
                return(False)
        else:
            return(val)

    def dumpdb(self):
        """Dump DB contents"""
        for row in self.conn.iterdump():
            print(row)
        

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check Web links with DB cache")
    #parser.add_argument('address', nargs='+', help='URL to check')
    parser.add_argument('--timeout', type=float, default=1.0, help='Time to wait for response')
    #parser.add_argument('--website', help='Force website for relative links')
    args = parser.parse_args()
    CL = checklinkdb(args.timeout)
    #if args.website:
    #    CL.setWebsite(args.website)
    #for address in args.address:
    #    print(CL.check(address))
    #CL.updatelinkinfo("http://web.mit.edu", 1)
    #print(CL.getlinkstatus("http://web.mit.edu"))
    #print(CL.getlinkstatus("http://www.mit.edu"))
