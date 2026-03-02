import requests
import json
import csv

# 1. Ссылка на CSV из Google Sheets (Файл -> Поделиться -> Опубликовать в интернете -> Значения, разделенные запятыми)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def build():
    response = requests.get(SHEET_CSV_URL)
    response.encoding = 'utf-8'
    reader = csv.DictReader(response.text.splitlines())
    items = list(reader)

    cards_html = ""
    for idx, item in enumerate(items):
        cards_html += f'''
        <div class="product-card" onclick="openModal({idx})">
            <img src="{item['img']}" class="product-img" loading="lazy">
            <div class="product-info">
                <div class="product-title">{item['name']}</div>
                <div class="product-price">{item['price']} ₽</div>
            </div>
        </div>'''

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    final_html = template.replace('{items_html}', cards_html)
    final_html = final_html.replace('{items_json}', json.dumps(items, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    build()
