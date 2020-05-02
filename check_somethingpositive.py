#!/usr/bin/python3
import decimal
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
        self.numpages = len(self.hrefs)
        logger.warning("Number of pages to check: %d" % self.numpages)
        website = 'https://somethingpositive.net'
        self.checker.setWebsite(website)
        logger.info("Setting base URL for relative links to %s" % website)

    def checkpages(self,numpages=None):
        logger = self.logger
        comicpages = [self.checker.fullurl(comicref) for comicref in self.hrefs]
        pagecount = 1
        if numpages:
            logger.warning(f"OVERRIDE:  Checking only {numpages} comicpages.")
        for comicpage in comicpages:
            logger.info(f"checking page: {comicpage}")
            pagehrefs = get_hrefs(comicpage)
            logger.debug(f"contains links: {pagehrefs}")
            for link in pagehrefs:
                live = self.checker.check(link)
                if live: logger.debug(f"{link} is LIVE")
                else: logger.warning(f"comicpage {comicpage} contains {link} which is DEAD")
            progress = decimal.Decimal(pagecount/float(self.numpages))*100
            print(f"{pagecount}/{self.numpages} = {progress:{4}.{3}}%", end="\r",flush=True)
            pagecount += 1
            if numpages and pagecount > numpages:
                print()
                break
        
        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check SomethingPositive links")
    parser.add_argument('website', help='SP archive website or page')
    parser.add_argument('--comicpage', action='store_true', help='address for page, not archive')
    parser.add_argument('--numpages', type=int, default=None, help='number of pages to check')
    args = parser.parse_args()    
    SPA = sparchives(args.website)
    SPA.checkpages(args.numpages)
    SPA.logger.warning("Processing complete")
