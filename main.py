import bs4
import logging
from fake_useragent import UserAgent
import requests
import collections

logger = logging.getLogger('copa')
logging.basicConfig(level=logging.DEBUG)

ua = UserAgent()
headers = {'User-Agent': ua.random}
ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url'
    ),
)
class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers
        self.result = []
    def load_page(self, page: int = None):
        url = 'https://www.copa.com.ua/index.php?route=product/search&search=joma&limit=100&page=1'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product-layout.product-grid.col-lg-4.col-md-4.col-sm-6.col-xs-12')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        logger.info(block)
        logger.info('=' * 100)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)

if __name__ == '__main__':
    parser = Client()
    parser.run()
