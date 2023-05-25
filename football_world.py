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
        'sizes',
        'availability',
        'main_image_url',
        'additional_image_urls',
        'description',
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
            price_new_elem = card.select_one('.product-cart__price-current')
            price_new = price_new_elem.text.strip() if price_new_elem else None

            # Парсим дополнительную информацию с URL товара
            additional_info = self.parse_additional_info(url)
            if additional_info is None:
                continue

            # Создаем экземпляр ParseResult и добавляем его в список результатов
            self.result.append(ParseResult(
                goods_name=goods_name,
                url=url,
                price_old=None,
                price_new=price_new,
                brand=additional_info['brand'],
                model=additional_info['model'],
                sizes=additional_info['sizes'],
                availability=additional_info['availability'],
                main_image_url=additional_info['main_image_url'],
                additional_image_urls=additional_info['additional_image_urls'],
                description=additional_info['description'],

            ))

        return True

    def parse_additional_info(self, url):
        try:
            res = self.session.get(url)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.content, 'html.parser')

            brand_elem = soup.select_one('div.wstabs-block table tr:first-child td:last-child')
            brand = brand_elem.text.strip() if brand_elem else None
            div_element = soup.select_one('.product-images__article')
            value = div_element.text.strip()
            start_index = value.find(':') + 1
            model = value[start_index:].strip() if value[start_index:] else None
            select_element = soup.find('select', {'name': 'size'})
            if select_element:
                options = select_element.find_all('option')
                sizes = [option.text.strip() for option in options[:-1] if option.get('value')]
            else:
                sizes = None
            availability_el = soup.select_one('.product-available__text')
            availability = availability_el.text.strip() if availability_el else None
            img_element = soup.select_one('img.product-images__main-slide')
            main_image_url = "https://football-world.com.ua" + img_element['src'] if img_element['src'] else None
            additional_image_urls = None
            description_el = soup.select_one('div.wstabs-block')
            p_tags = description_el.find_all('p')

            if len(p_tags) > 0:
                last_p_tag = p_tags[-1]
                description = last_p_tag.text.strip()
            else:
                description = None

            additional_info = {
                'brand': brand,
                'model': model,
                'sizes': sizes,
                'availability': availability,
                'main_image_url': main_image_url,
                'additional_image_urls': additional_image_urls,
                'description': description,
            }
            return additional_info
        except requests.exceptions.HTTPError as e:
            logger.error(f'Ошибка при загрузке страницы {url}: {e}')
            return None

    def save_results(self):
        with open('football_world_test_results.csv', 'w', newline='', encoding='utf-8') as f:
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
