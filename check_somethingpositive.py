#!/usr/bin/python3
import decimal
import sys
import os.path
import datetime
import argparse
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse,urlunparse

import checklink


if __name__ == '__main__':
    # http://stackoverflow.com/questions/8299270/ultimate-answer-to-relative-python-imports
    # relative imports do not work when we run this module directly
    PACK_DIR = os.path.dirname(os.path.join(os.getcwd(), __file__))
    ADDTOPATH = os.path.normpath(os.path.join(PACK_DIR, '..'))
    # add more .. depending upon levels deep
    sys.path.append(ADDTOPATH)

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))


    
class sparchives():
    checker = checklink.checklink(timeout=2.0)
    logger = logging.getLogger("app")
    def __init__(self,address,single_comicpage=False):
        website = 'https://somethingpositive.net'
        self.checker.setWebsite(website)

        logger = self.logger        
        logger.setLevel(logging.DEBUG)
        dt = datetime.datetime.today()
        timestamp = dt.strftime("%Y%m%d-%H%M%S")
        urlpath = urlparse(address).path
        # now remove anything we don't need
        pagename = os.path.basename(urlpath)
        rootname = os.path.splitext(pagename)[0]
        
        logpath = f"check-{rootname}-{timestamp}.log"
        logger.addHandler(logging.FileHandler(logpath))
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
        logger.warning("Logging to %s", logpath)

        logger.info("Setting base URL for relative links to %s" % website)

        self.address=address
        logger.warn("Top level URL: %s" % address)
        if not single_comicpage:
            self.hrefs=self.get_hrefs(address)
            logger.info("Links on archive page: %s" % self.hrefs)
            self.numpages = len(self.hrefs)
            logger.warning("Number of pages to check: %d" % self.numpages)

    def get_hrefs(self,address,prefix='sp'):
        """Grab a page, parse it, and rip out the right hrefs. OH, and check somethings"""
        r = requests.get(address)
        soup = BeautifulSoup(r.text, 'html.parser')
        retval = []
        #print(soup.prettify())
        #next_link = soup.findAll('a',href=True,text='Previous<br>Comic')
        #print(next_link)
        for link in soup.find_all('a'):
            linkhref = link.get('href')
            linktext = link.text
            #print (f"link:  {linkhref} which has text '{linktext}'")
            if linktext.lower() == 'previouscomic':
                if self.checker.fullurl(linkhref) == address:
                    self.logger.error(f"ERROR: comicpage {address} link to previous comic is current comic")
            if linktext.lower() == 'nextcomic':
                if self.checker.fullurl(linkhref) == address:
                    self.logger.error(f"ERROR: comicpage {address} link to next comic is current comic")
            if linkhref is None:
                self.logger.error(f"ERROR: comicpage {address} has a broken HREF: {link}.")                
            elif linkhref.startswith(prefix) and linkhref.endswith('.shtml'):
                retval.append(linkhref)
        return retval


    def checkpages(self,numpages=None,single_comicpage=False):
        logger = self.logger
        comicpages = []
        if single_comicpage:
            comicpages = [self.checker.fullurl(self.address)]  ## we were given the comicpage

        else:
            comicpages = [self.checker.fullurl(comicref) for comicref in self.hrefs]
        pagecount = 1
        if numpages:
            logger.warning(f"OVERRIDE:  Checking only {numpages} comicpages.")
        for comicpage in comicpages:
            logger.info(f"checking page: {comicpage}")
            pagehrefs = self.get_hrefs(comicpage)
            logger.debug(f"contains links: {pagehrefs}")
            if single_comicpage:
                self.numpages = len(pagehrefs)
                logger.warning("Number of links to check: %d" % self.numpages)

            for link in pagehrefs:
                live = self.checker.check(link)
                if live: logger.debug(f"{link} is LIVE")
                else: logger.warning(f"ERROR: comicpage {comicpage} contains {link} which is DEAD")
            progress = decimal.Decimal(pagecount/float(self.numpages))*100
            print(f"{pagecount}/{self.numpages} = {progress:{4}.{3}}%", end="\r",flush=True)
            pagecount += 1
            if numpages and pagecount > numpages:
                print()
                break
        
        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Check SomethingPositive links")
    parser.add_argument('website', help='SP archive or comicpage')
    parser.add_argument('--comicpage', action='store_true', help='address for page, not archive')
    parser.add_argument('--numpages', type=int, default=None, help='number of pages to check')
    args = parser.parse_args()    
    SPA = sparchives(args.website,single_comicpage=args.comicpage)
    SPA.checkpages(args.numpages,single_comicpage=args.comicpage)
    SPA.logger.warning("Processing complete")
