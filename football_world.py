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
# ParseResult = collections.namedtuple(
#     'ParseResult',
#     (
#         'goods_name',
#         'url',
#         'price_old',
#         'price_new',
#         'brand',
#         'model',
#         'sizes',
#         'availability',
#         'main_image_url',
#         'additional_image_urls',
#         'description',
#     ),
# )
#
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
        url =  f'https://football-world.com.ua/ru/search?search={MANUFACTURER}&page={page}'
        res = self.session.get(url)
        res.raise_for_status()
        return res.content

    def parse_page(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        cards = soup.select('.catalog__item')
        if not cards:
            return False

        for card in cards:

            # Извлекаем основную информацию о товаре
            goods_name_elem = card.select_one('.product-cart__title')
            goods_name = goods_name_elem.text.strip()
            url = goods_name_elem['href']
            price_old_elem = card.select_one('.product-cart__price-old')
            price_old = price_old_elem.text.strip() if price_old_elem else None
            print(price_old)
            price_new_elem = card.select_one('.product-cart__price-current')
            price_new = price_new_elem.text.strip() if price_new_elem else None
            print(price_new)

            # Парсим дополнительную информацию с URL товара
            # additional_info = self.parse_additional_info(url)
            # if additional_info is None:
            #     continue

            # Создаем экземпляр ParseResult и добавляем его в список результатов
            # self.result.append(ParseResult(
            #     goods_name=goods_name,
            #     url=url,
            #     price_old=None,
            #     price_new=price_new,
            #     brand=additional_info['brand'],
            #     model=additional_info['model'],
            #     sizes=additional_info['sizes'],
            #     availability=additional_info['availability'],
            #     main_image_url=additional_info['main_image_url'],
            #     additional_image_urls=additional_info['additional_image_urls'],
            #     description=additional_info['description'],
            #
            # ))

        # return True

    # def parse_additional_info(self, url):
    #     try:
    #         res = self.session.get(url)
    #         res.raise_for_status()
    #         soup = bs4.BeautifulSoup(res.content, 'html.parser')
    #
    #         brand_elem = soup.select_one('.product-tabs__properties a')
    #         brand = brand_elem.text.strip() if brand_elem else None
    #         model_el = soup.select_one('.changemodel')
    #         model = model_el.text.strip() if model_el else None
    #         sizes_elems = soup.select('.product__mobile-size-list')
    #         sizes = [size_elem.text.strip() for size_elem in sizes_elems[0].find_all('li')] if sizes_elems else None
    #         availability_el = soup.select_one('.product__aviability ')
    #         availability = availability_el.text.strip() if availability_el else None
    #         main_image_elem = soup.select_one('.thumbnail')
    #         main_image_url = main_image_elem['href'] if main_image_elem else None
    #         additional_image_el = soup.select('.product__gallery-m-nav-slide img')
    #         additional_image_urls = [img['src'] for img in additional_image_el[1:]] if additional_image_el else None
    #         description_el = soup.select_one('div.product-tabs__description')
    #         description = description_el.text.strip() if description_el else None
    #
    #         additional_info = {
    #             'brand': brand,
    #             'model': model,
    #             'sizes': sizes,
    #             'availability': availability,
    #             'main_image_url': main_image_url,
    #             'additional_image_urls': additional_image_urls,
    #             'description': description,
    #         }
    #         return additional_info
    #     except requests.exceptions.HTTPError as e:
    #         logger.error(f'Ошибка при загрузке страницы {url}: {e}')
    #         return None

    def save_results(self):
        with open('hunter_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        logger.info('Загрузка страницы...')
        page = 1
        self.start_time = time.time()

        # while True:
        logger.info(f'Парсинг страницы {page}...')
        html = self.load_page(page)
        has_next_page = self.parse_page(html)
        logger.info(f'Сохранение результатов страницы {page}...')

        # Засекаем время отработки и выводим в терминал
        elapsed_time = time.time() - self.start_time
        logger.info(f'Время парсинга текущей страницы: {elapsed_time:.2f} секунд')

        self.save_results()

            # if not has_next_page:
            #     self.total_time = time.time() - self.start_time
            #     logger.info(f'Общее время парсинга всех страниц: {self.total_time:.2f} секунд')
            #     break
            #
            # page += 1
            # time.sleep(3)  # Тайм-аут в 3 секунды

        logger.info('Готово!')


if __name__ == '__main__':
    client = Client()
    client.run()
