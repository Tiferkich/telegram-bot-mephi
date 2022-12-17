import requests
from bs4 import BeautifulSoup
import re

r=requests.get("https://coinmarketcap.com/")
html = BeautifulSoup(r.content,'html.parser')
data = html.find('class',{'class':'priceValue ' }).text

print(data)