import bs4
import logging
from fake_useragent import UserAgent
import requests
import collections
import csv

logger = logging.getLogger('copa')
logging.basicConfig(level=logging.INFO)

ua = UserAgent()
headers = {'User-Agent': ua.random}
ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'goods_name',
        'url',
        'price_old',
        'price_new',
        'brand',
        'model',
        'sizes',
        'availability',
        'main_image_url',
        'additional_image_urls',
        # 'description',
        # 'material',
        # 'color',
        # 'gender',
    ),
)

HEADERS = (
    'Назва',
    'Посилання',
    'Стара ціна',
    'Нова ціна',
    'Бренд',
    'Модель',
    'Розміри',
    'Наявність',
    'Посилання на основне зображення',
    'Посилання на додаткові зображення',
    'Опис',
    'Матеріал',
    'Колір',
    'Стать',
)

PAGE = 1


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers
        self.result = []

    def load_page(self, page: int = None):
        url = f'https://www.copa.com.ua/index.php?route=product/search&search=joma&limit=12&page={PAGE}'
        res = self.session.get(url)
        res.raise_for_status()
        return res.content

    def parse_page(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        cards = soup.select('.product-layout')

        for card in cards:
            # Извлекаем основную информацию о товаре
            goods_name_elem = card.select_one('.caption span.h4 a')
            goods_name = goods_name_elem.text.strip()
            url = goods_name_elem['href']
            price_new_elem = card.select_one('.price .price-new')
            if price_new_elem:
                price_new = price_new_elem.text.strip()
                price_old_elem = card.select_one('.price .price-old')
                if price_old_elem:
                    price_old = price_old_elem.text.strip()
                else:
                    price_old = None
            else:
                price_elem = card.select_one('.price')
                price_new = price_elem.text.strip()
                price_old = None

            # Парсим дополнительную информацию с URL товара
            additional_info = self.parse_additional_info(url)

            # Создаем экземпляр ParseResult и добавляем его в список результатов
            self.result.append(ParseResult(
                goods_name=goods_name,
                url=url,
                price_old=price_old,
                price_new=price_new,
                brand=additional_info['brand'],
                model=additional_info['model'],
                sizes=additional_info['sizes'],
                availability=additional_info['availability'],
                main_image_url=additional_info['main_image_url'],
                additional_image_urls=additional_info['additional_image_urls'],
                # description=additional_info['description'],
                # material=additional_info['material'],
                # color=additional_info['color'],
                # gender=additional_info['gender'],
            ))

    def parse_additional_info(self, url):
        res = self.session.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.content, 'html.parser')

        brand = brand_elem.text.strip() if (brand_elem := soup.select_one('span[itemprop="brand"]')) else None
        model = model_elem.text.strip() if (
            model_elem := soup.select_one('div.bg-white.list-info span:-soup-contains("Модель:") + span')) else None
        sizes_elems = soup.select('.form-group.select-option select option')
        sizes = [size_elem.text.strip() for size_elem in sizes_elems[1:] if
                 size_elem.text.strip()] if sizes_elems else None
        availability = (div_elem.text.replace(span_elem.text, '').strip() if (
            div_elem := span_elem.find_parent('div')) else None) if (
            span_elem := soup.find('span', class_='width-margin', string='Наличие:')) else None
        main_image_url = soup.select_one('.thumbnails a.thumbnail')['href']
        additional_image_urls = [img['href'] for img in soup.select('.thumbnails li.image-additional a.thumbnail')] or None

        description = soup.select_one('.tab-pane#tab-description div.product-description').text.strip()
        material = soup.select_one('#tab-specification table.table td:contains("Матеріал:")').find_next(
            'td').text.strip()
        color = soup.select_one('#tab-specification table.table td:contains("Колір:")').find_next('td').text.strip()
        gender = soup.select_one('[itemprop="category"]').text.strip()

        additional_info = {
            'brand': brand,
            'model': model,
            'sizes': sizes,
            'availability': availability,
            'main_image_url': main_image_url,
            'additional_image_urls': additional_image_urls,
            # 'description': description,
            # 'material': material,
            # 'color': color,
            # 'gender': gender,
        }
        return additional_info

    def save_results(self):
        with open('copa_results.csv', 'w', newline='', encoding='utf-8') as f:

            writer = csv.writer(f)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        logger.info('Загрузка страницы...')
        page = self.load_page(PAGE)
        logger.info('Парсинг страницы...')
        self.parse_page(page)
        logger.info('Сохранение результатов...')
        self.save_results()
        logger.info('Готово!')


if __name__ == '__main__':
    client = Client()
    client.run()
