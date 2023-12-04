import datetime
import sys

import xml.etree.ElementTree as etree

import requests
from bs4 import BeautifulSoup
from defusedxml import minidom
from lxml import etree as et
from lxml.etree import tostring

req = requests.get('https://drevodesign.ru/product/stoly/zhurnalnye-stoly/')
soup = BeautifulSoup(req.text, 'lxml')
src_pages = soup.find(class_='pagination').find_all('a')
src_pages = ['https://drevodesign.ru' + a.get('href') for a in src_pages]
src_pages = src_pages[:-1]
src_pages.append('https://drevodesign.ru/product/stoly/zhurnalnye-stoly/')
data = {}
for src_page in src_pages:
    products_on_page = []
    req = requests.get(src_page)
    soup = BeautifulSoup(req.text, 'lxml')
    catalog = soup.find(class_='section-content-wrapper')
    all_product = catalog.find_all(class_='item')
    for product in all_product:
        if product != None:
            name = product.find('span').text
            sku = product.find(class_='article').text.split('\xa0')[1]
            src = 'https://drevodesign.ru' + product.find('a').get('href')
            img = 'https://drevodesign.ru' + product.find('img').get('src')
            price = product.find(class_='price_val').text
            is_avail = soup.find(class_='status-icon instock')
            if is_avail == None:
                is_avail = soup.find(class_='status-icon order')
            is_avail = is_avail.text
            if is_avail == 'В наличии':
                is_avail = 'Да'
            else:
                is_avail = 'Под заказ'
            products_on_page.append([name, sku, src, img, price, is_avail])
    data[src_page] = products_on_page
print(data)
turbo = 'http://turbo.yandex.ru'
yandex = "http://news.yandex.ru"
media = "http://search.yahoo.com/mrss/"
NS_MAP = {'yandex': yandex,
          "media": media,
          'turbo': turbo}

root = et.Element('rss', nsmap=NS_MAP)
sheet = et.ElementTree(root)

root.set('version', '2.0')

channel = et.SubElement(root, 'channel')
for key in data.keys():
    print(key)
    item = et.SubElement(channel, 'item')
    item.set('turbo', 'true')
    link = et.SubElement(item, 'link')
    title = et.SubElement(item, 'title')
    title.text = 'Журнальные столы'
    link.text = key
    category = et.SubElement(item, 'category')
    category.text = 'Журнальные столы'
    turboContent = et.SubElement(item, et.QName(turbo, 'content'))
    text = ''
    for product in data[key]:
        str = f'''
        <figure> <img src={product[3]}> </figure> 
        <h1>{product[0]} </h1>
        <p>
        <b>Цена: </b>
        от {product[4]} руб.
        </p>
        <p>
        <b>В наличии: </b>
        {product[5]}
        </p>
        <p>
        <b>Артикул: </b>
        {product[1]}
        </p>
        <a href={product[2]}> Узнать больше </a>
        '''
        text += str
    tmp = et.Element('temp')
    tmp.text = et.CDATA(text)
    turboContent.text = et.tostring(tmp, encoding="unicode").replace('</temp>', '').replace('<temp>', '')
    print(tostring(turboContent, encoding="unicode"))

xml_string = et.tostring(sheet).decode()
xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
with open("rss.xml", 'w', encoding="utf-8") as xml_file:
    xml_file.write(xml_prettyxml)
tree = et.parse("rss.xml")
root = tree.getroot()
tree.write("rss.xml", encoding='utf-8', xml_declaration=True)
