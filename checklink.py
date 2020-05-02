#!/usr/bin/python3
"""Class to check if a URL is live or not
Caches results to speed up processing.
By Joseph T. Foley <foley AT RU.IS>  
Created 2020-05-02
MIT License
"""
import argparse
import requests
import time
from urllib.parse import urlparse,urlunparse

class checklink():
    LIVE = {}
    DEAD = {}
    timeout = 1
    website = ""
    def __init__(self, timeout=None):
        """Setup important instance variables"""
        if not timeout: self.timeout = timeout

    def setWebsite(self,address):
        """Examine the main website and parse it into reusable parts"""
        websiteinfo = urlparse(address)
        self.scheme = websiteinfo.scheme
        self.netloc = websiteinfo.netloc
    def fullurl(self,address):
        """Return a full URL if it is just a relative link"""
        urlinfo = urlparse(address)
        #print(urlinfo)           
        if urlinfo.netloc is '':## grab from website
            urlinfo = urlinfo._replace(scheme = self.scheme)
            urlinfo = urlinfo._replace(netloc = self.netloc)
            #print(urlinfo)
        address = urlunparse(urlinfo)
        #print(address)
        return(address)

    def check(self,address):
        "see if a URL is live or not"
        address=self.fullurl(address)
        if address in self.LIVE:
            return True
        if address in self.DEAD:
            return False
        #print("checking %s" % address)
        try:
            r = requests.get(address, timeout=self.timeout)
            self.LIVE[address] = time.gmtime()
            return True
        except requests.exceptions.RequestException:
            self.DEAD[address] = time.gmtime()
            return False
            

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check Web links")
    parser.add_argument('address', nargs='+', help='URL to check')
    parser.add_argument('--timeout', type=float, default=1.0, help='Time to wait for response')
    parser.add_argument('--website', help='Force website for relative links')
    args = parser.parse_args()
    CL = checklink(args.timeout)
    if args.website:
        CL.setWebsite(args.website)
    for address in args.address:
        print(CL.check(address))
    
