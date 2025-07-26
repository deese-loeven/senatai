import requests
from bs4 import BeautifulSoup

url = 'https://www.ola.org/en/legislative-business/bills/current'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Successfully fetched {len(soup.find_all('a'))} links from Ontario Legislature website")  
