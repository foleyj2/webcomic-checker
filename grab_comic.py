import requests
from bs4 import BeautifulSoup

r = requests.get("https://somethingpositive.net/sp01272010.shtml")
soup = BeautifulSoup(r.text, 'html.parser')
#print(soup.prettify())
for link in soup.find_all('a'):
    linkhref = link.get('href')
    if linkhref.startswith('sp'):
        print(linkhref)
    
