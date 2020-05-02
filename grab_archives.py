import requests
from bs4 import BeautifulSoup

class archives():
    def __init__(self,address):
        self.address=address
    def check(self,address=None):
        if address is None:
            address = self.address
        r = requests.get(address)
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup.prettify())
        for link in soup.find_all('a'):
            linkhref = link.get('href')
            if linkhref.startswith('sp'):
                print(linkhref)

if __name__=="__main__":
    website=input("URL: ")
    CL = check_link(website)
    CL.check()
