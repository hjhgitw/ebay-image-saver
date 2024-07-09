from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import os
import zipfile
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_images', methods=['POST'])
def save_images():
    url = request.form['url']
    try:
        response = requests_retry_session().get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')
    image_urls = [img['src'] for img in images]

    if not os.path.exists('images'):
        os.makedirs('images')

    for i, img_url in enumerate(image_urls):
        try:
            img_response = requests_retry_session().get(img_url)
            img_response.raise_for_status()
            with open(f'images/image_{i}.jpg', 'wb') as f:
                f.write(img_response.content)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download image {img_url}: {e}")

    with zipfile.ZipFile('images.zip', 'w') as zipf:
        for root, dirs, files in os.walk('images'):
            for file in files:
                zipf.write(os.path.join(root, file))

    return send_file('images.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(port=8881)