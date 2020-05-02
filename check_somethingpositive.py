#!/usr/bin/python3
import argparse
import requests
from bs4 import BeautifulSoup

def get_hrefs(address,prefix='sp'):
    r = requests.get(address)
    soup = BeautifulSoup(r.text, 'html.parser')
    retval = []
    #print(soup.prettify())
    for link in soup.find_all('a'):
        linkhref = link.get('href')
        if linkhref.startswith(prefix) and linkhref.endswith('.shtml'):
            retval.append(linkhref)
    return retval

## TODO:  store checks in a dictionary to minimize number of network accesses
    
class sparchives():
    def __init__(self,address):
        self.address=address
        self.hrefs=get_hrefs(address)
        self.website='https://somethingpositive.net'
    def fulllink(self,ref):
        """Turn a relative link into a full URL"""
        return("%s/%s" % (self.website,ref))
        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check SomethingPositive links")
    parser.add_argument('website', help='SP archive website')
    args = parser.parse_args()    
    SPA = sparchives(args.website)
    comicpages = [SPA.fulllink(comicref) for comicref in SPA.hrefs]
    for comicpage in comicpages:
        print("page: %s"%comicpage)
        pagehrefs = get_hrefs(comicpage)
        print(pagehrefs)
