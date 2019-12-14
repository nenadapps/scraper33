from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_info_value(html, heading):
    
    value = ''
    
    try:
        for item in html.select('.shop_attributes th'):
            item_heading = item.get_text().strip()
            item_value = item.find_next().get_text().strip()
            if item_heading == heading:
                value = item_value
                break
    except: 
        pass
    
    return  value

def get_details(url, category):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('.summary-inner .woocommerce-Price-amount')[0].get_text().strip()
        stamp['price'] = price.replace('£', '').replace(',', '').strip()
    except: 
        stamp['price'] = None
        
    try:
        title = html.select('.product_title')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None
    
    try:
        raw_text = html.select('.summary-inner p')[1].get_text().strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None    
        
    type_value = ''  
    try:
        counter = 0
        for breadcrumb_item in html.select('.woocommerce-breadcrumb a'):
            if counter > 1:
                if type_value:
                    type_value += ' / ' 
                type_value += breadcrumb_item.get_text().strip()    
            counter = counter + 1
    except:
        pass
    
    stamp['type'] = type_value
    
    stamp['sku'] = get_info_value(html, 'SKU')
    cat_num = get_info_value(html, 'SG Number')
    if not cat_num:
        cat_num = get_info_value(html, 'Catalogue Number')
    stamp['cat_num'] = cat_num
    
    stamp['category'] = category   

    stamp['currency'] = 'GBP'

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.woocommerce-product-gallery__image a')
        for image_item in image_items:
            img = image_item.get('href')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):
    
    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item_cont in html.select('.product-title'):
            item_link = item_cont.select('a')[0].get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url = html.select('a.next')[0].get('href')
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_categories():
    
    url = 'https://www.andrewglajer.co.uk/whats-new/'
    
    items = {}

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item_cont in html.select('#menu-new-main-menu > li > a'):
            item_link = item_cont.get('href')
            item_name = item_cont.get_text().strip()
            if ((item_link not in items) and (item_name != 'New')): 
                items[item_name] = item_link
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

categories = get_categories()
for category_name in categories:
    category = categories[category_name]
    page_url = category
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item, category_name)

