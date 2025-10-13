import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.ola.org"

def get_bill_links():
    url = "https://www.ola.org/en/legislative-business/bills"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    bill_links = []
    for link in soup.select('a[href^="/en/legislative-business/bills/"]'):
        if link['href'].count('/') == 5:  # This filters only individual bill pages
            bill_links.append(BASE_URL + link['href'])
    
    return bill_links
