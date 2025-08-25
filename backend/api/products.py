from fastapi import APIRouter, Query
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import time

router = APIRouter(prefix="/products", tags=["products"])

FEED_URL = "https://elakstron.com.ua/products_feed.xml?hash_tag=738e9d3de8981c596e348b68ef6677ee&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&extra_fields=quantityInStock%2Ckeywords&group_ids="

# Простий кеш у пам'яті
_cache = {"data": [], "timestamp": 0}
CACHE_TTL = 60 * 60  # 1 година

def fetch_products() -> List[Dict]:
    now = time.time()
    if now - _cache["timestamp"] < CACHE_TTL and _cache["data"]:
        return _cache["data"]
    response = requests.get(FEED_URL)
    response.encoding = 'utf-8'
    root = ET.fromstring(response.text)
    products = []
    for offer in root.findall('.//offer'):
        product = {
            'id': offer.get('id'),
            'name': offer.findtext('name_ua', default=''),  # українська назва
            'price': offer.findtext('price', default=''),
            'quantity': offer.findtext('quantityInStock', default=''),
            'vendor': offer.findtext('vendor', default=''),
            'url': offer.findtext('url', default=''),
            'picture': offer.findtext('picture', default=''),
            'articul': offer.findtext('vendorCode', default=''),  # артикул
        }
        products.append(product)
    _cache["data"] = products
    _cache["timestamp"] = now
    return products

@router.get("/")
def search_products(q: str = Query('', description="Пошук по назві, id або артикулу")):
    products = fetch_products()
    if q:
        ql = q.lower()
        products = [p for p in products if ql in p['name'].lower() or ql in str(p['id']).lower() or ql in p['articul'].lower()]
    return products[:20]