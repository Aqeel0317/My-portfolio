import requests
from bs4 import BeautifulSoup

url = "https://www.longi.com/en/modules-authenticity/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Example: Print the title of the page
print(soup.title.text)

# Example: Find all links
for link in soup.find_all('a'):
    print(link.get('href'))