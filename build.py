import requests
import json
import csv

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def build():
    response = requests.get(SHEET_CSV_URL)
    response.encoding = 'utf-8'
    reader = csv.DictReader(response.text.splitlines())
    items = list(reader)

    # Группируем блюда по категориям
    categories = {}
    for item in items:
        cat = item.get('category', 'Разное')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    # Генерируем HTML для навигации (кнопки сверху)
    nav_html = ""
    sections_html = ""
    
    # Чтобы передать данные в JS, нам нужен плоский список с сохранением порядка
    flat_items_for_js = []
    global_idx = 0

    for cat_name, cat_items in categories.items():
        # Кнопка в меню
        cat_id = f"cat-{hash(cat_name)}"
        nav_html += f'<a href="#{cat_id}" class="nav-item">{cat_name}</a>'
        
        # Секция с карточками
        sections_html += f'<h2 id="{cat_id}" class="category-title">{cat_name}</h2>'
        sections_html += '<div class="menu-grid">'
        for item in cat_items:
            # Проверяем наличие цены. Если цена есть, формируем строку с символом ₽
            price_val = item.get('price')
            price_html = f'<div class="product-price">{price_val} ₽</div>' if price_val else ''
            # Проверяем наличие картинки для src. если пусто, атрибут src будет пустым, а CSS его скроет
            img_src = item.get('img', '')
            
            sections_html += f'''
            <div class="product-card" onclick="openModal({global_idx})">
                <img src="{item['img']}" class="product-img" loading="lazy">
                <div class="product-info">
                    <div class="product-title">{item['name']}</div>
                    {price_html}
                </div>
            </div>'''
            flat_items_for_js.append(item)
            global_idx += 1
        sections_html += '</div>'

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    final_html = template.replace('{nav_items}', nav_html)
    final_html = final_html.replace('{sections_html}', sections_html)
    final_html = final_html.replace('{items_json}', json.dumps(flat_items_for_js, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    build()
