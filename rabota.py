# -*- coding: utf-8 -*-
import time

from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


chrome_driver_path = r"E:\development prog\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = 'https://rabota.ua/ua/zapros/python/%D0%BA%D0%B8%D0%B5%D0%B2?page=1'
driver.get(url)
html_page = driver.page_source

soup = BS(html_page, 'lxml')
vacancy_cards = soup.find_all('a', class_='card')

for card in vacancy_cards:
    vacancy_link = card['href']
    vacancy_title_el = card.find('h2')
    vacancy_title = vacancy_title_el.text.strip() if vacancy_title_el else 'No vacancy'
    employer_name = card.find('span', class_='santa-mr-20').text if card.find('span',
                                                                              class_='santa-mr-20') else 'Noname employer'
    description = card.find('p', class_='santa-typo-additional').text.strip() if card.find('p',
                                                                                           class_='santa-typo-additional') else 'No description'
    # location = card.find('span', class_='ng-tns-c187-6').text if card.find('span', class_='ng-tns-c187-6').text else 'Noname city'
    print('Посилання: ', vacancy_link)
    print('Назва: ', vacancy_title)
    print('Роботодавець: ', employer_name)
    print('Опис вакансії: ', description)
    # print('Місто: ', location)
    print()


driver.quit()
