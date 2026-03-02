import requests
import json

# 1. Ссылка на CSV из Google Sheets (Файл -> Поделиться -> Опубликовать в интернете -> Значения, разделенные запятыми)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def build():
    # Качаем данные
    r = requests.get(SHEET_CSV_URL)
    r.encoding = 'utf-8'
    lines = r.text.splitlines()
    
    import csv
    reader = csv.DictReader(lines)
    items = list(reader)

    # Генерируем HTML карточек (SSR)
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

    # Читаем шаблон и заменяем метки
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    final_html = template.replace('{items_html}', cards_html)
    final_html = final_html.replace('{items_json}', json.dumps(items, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("Сайт успешно собран в index.html!")

build()
