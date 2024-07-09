import requests
from bs4 import BeautifulSoup
import os

def save_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    os.makedirs('images', exist_ok=True)
    for i, img in enumerate(img_tags):
        img_url = img.get('src')
        img_data = requests.get(img_url).content
        with open(f'images/image_{i+1}.jpg', 'wb') as handler:
            handler.write(img_data)
    return f'{len(img_tags)} images downloaded.'

if __name__ == '__main__':
    url = input('Enter eBay offer URL: ')
    print(save_images(url))