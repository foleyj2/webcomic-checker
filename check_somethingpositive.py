#!/usr/bin/python3
import sys
import os.path
import datetime
import argparse
import requests
from bs4 import BeautifulSoup
import checklink
import logging

if __name__ == '__main__':
    # http://stackoverflow.com/questions/8299270/ultimate-answer-to-relative-python-imports
    # relative imports do not work when we run this module directly
    PACK_DIR = os.path.dirname(os.path.join(os.getcwd(), __file__))
    ADDTOPATH = os.path.normpath(os.path.join(PACK_DIR, '..'))
    # add more .. depending upon levels deep
    sys.path.append(ADDTOPATH)

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))


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
    
class sparchives():
    checker = checklink.checklink(timeout=2.0)
    logger = logging.getLogger("app")
    def __init__(self,address):
        logger = self.logger        
        logger.setLevel(logging.DEBUG)
        dt = datetime.datetime.today()
        logpath = "sp-check-%s.log" % dt.strftime("%Y%m%d-%H%M%S")
        logger.addHandler(logging.FileHandler(logpath))
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
        logger.info("Logging to %s", logpath)

        self.address=address
        logger.warn("Top level archive URL: %s" % address)
        self.hrefs=get_hrefs(address)
        logger.info("Links on archive page: %s" % self.hrefs)
        website = 'https://somethingpositive.net'
        self.checker.setWebsite(website)
        logger.info("Setting base URL for relative links to %s" % website)

    def checkpages(self,numpages=None):
        logger = self.logger
        comicpages = [self.checker.fullurl(comicref) for comicref in self.hrefs]
        pagecount = 0
        for comicpage in comicpages:
            logger.info("checking page: %s" % comicpage)
            pagehrefs = get_hrefs(comicpage)
            logger.debug("contains links: %s" % pagehrefs)
            for link in pagehrefs:
                live = self.checker.check(link)
                if live: logger.debug("%s is LIVE" % link)
                else: logger.warning("comicpage %s contains %s which is DEAD" % (comicpage, link))
            print(".", end="",flush=True)
            pagecount += 1
            if numpages and pagecount >= numpages:
                break
        
        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check SomethingPositive links")
    parser.add_argument('website', help='SP archive website or page')
    parser.add_argument('--comicpage', help='address for page, not archive')
    parser.add_argument('--numpages', type=int, default=5, help='number of pages to check')
    args = parser.parse_args()    
    SPA = sparchives(args.website)
    SPA.checkpages(args.numpages)
    SPA.logger.warning("Processing complete")
