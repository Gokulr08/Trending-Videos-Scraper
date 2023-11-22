import requests
from bs4 import BeautifulSoup

url = 'https://www.youtube.com/feed/trending'

response = requests.get(url)

with open('html.txt', 'w', encoding='utf-8') as f:
  f.write(response.text)

doc = BeautifulSoup(response.text, 'html.parser')
print(doc.title.text)
