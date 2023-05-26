# -*- coding: utf-8 -*-


import bs4
import logging
import csv
import requests
from fake_useragent import UserAgent
import collections
import time


MANUFACTURER = 'joma'

logger = logging.getLogger('football_world')
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
        'availability',
        'main_image_url',
        'additional_image_urls',
    ),
)

HEADERS = (
    'Назва',
    'Посилання',
    'Стара ціна',
    'Нова ціна',
    'Бренд',
    'Модель',
    'Наявність',
    'Розміри',
    'Посилання на основне зображення',
    'Посилання на додаткові зображення',
    'Опис товару',
)


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers
        self.result = []
        self.start_time = None
        self.total_time = None

    def load_page(self, page):

        url = f'https://soccer-shop.com.ua/ua/m9-{MANUFACTURER}/page/{page}'
        res = self.session.get(url)
        res.raise_for_status()
        return res.content

    def parse_page(self, html):
        soup = bs4.BeautifulSoup(html, 'lxml')
        products = soup.select('.prod')[:20]
        if not products:
            return False


        for product in products:
            goods_name = product.select_one('.products-name a').text.strip()
            price_old_element = product.select_one('.price.old .int')
            price_old = price_old_element.text.strip() if price_old_element else ""
            price_new_element = product.select_one('.price.sale .int')
            price_new = price_new_element.text.strip() if price_new_element else ""
            availability_el = product.select_one('.products-quantity.instock')
            availability = availability_el.text.strip() if availability_el else ""
            url ='https://soccer-shop.com.ua' + product.select_one('.products-name a')['href']
            brand = product.select_one('.products-manufacturers-name').text.strip()
            model_el = product.select_one('.products-model span')
            model = model_el.text.strip() if model_el else ""
            # Парсим дополнительную информацию внутри карточки товара по URL
            additional_info = self.parse_additional_info(url)
            if additional_info is None:
                continue

            # Создаем экземпляр ParseResult и добавляем его в список результатов
            self.result.append(ParseResult(
                goods_name=goods_name,
                url=url,
                price_old=price_old,
                price_new=price_new,
                brand=brand,
                model=model,
                availability = availability,
                main_image_url=additional_info['main_image_url'],
                additional_image_urls=additional_info['additional_image_urls'],
            ))

        return True

    def parse_additional_info(self, url):
        try:
            res = self.session.get(url)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.content, 'lxml')

            img_tags = soup.select('.product-info-image.owl-carousel img')
            main_image_url = 'https://soccer-shop.com.ua' + img_tags[0]['src'] if img_tags else None
            additional_image_urls = ['https://soccer-shop.com.ua' + img['src'] for img in img_tags[1:]] if len(img_tags) > 1 else []

            additional_info = {
            'main_image_url': main_image_url,
            'additional_image_urls': additional_image_urls,

            }
            return additional_info
        except requests.exceptions.HTTPError as e:
            logger.error(f'Ошибка при загрузке страницы {url}: {e}')
            return None

    def save_results(self):
        with open('soccer_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        logger.info('Загрузка страницы...')
        page = 1
        self.start_time = time.time()

        while True:
            logger.info(f'Парсинг страницы {page}...')
            html = self.load_page(page)
            has_next_page = self.parse_page(html)
            logger.info(f'Сохранение результатов страницы {page}...')

            # Засекаем время отработки и выводим в терминал
            elapsed_time = time.time() - self.start_time
            logger.info(f'Время парсинга текущей страницы: {elapsed_time:.2f} секунд')

            self.save_results()

            if not has_next_page:
                self.total_time = time.time() - self.start_time
                logger.info(f'Общее время парсинга всех страниц: {self.total_time:.2f} секунд')
                break

            page += 1
            time.sleep(3)  # Тайм-аут в 3 секунды

        logger.info('Готово!')


if __name__ == '__main__':
    client = Client()
    client.run()
