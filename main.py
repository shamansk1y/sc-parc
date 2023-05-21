from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup


ua = UserAgent().random
headers = {'User-Agent': ua}

class Client:

    def __init__(self):
        self.session = requests.Session
        self.session.headers = {'User-Agent': ua}

    def load_page(self, page: int = None):
        url = 'https://www.copa.com.ua/index.php?route=product/search&search=joma&limit=100&page=1'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text