import requests
import json
import csv

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def build():
    response = requests.get(SHEET_CSV_URL)
    response.encoding = 'utf-8'
    reader = csv.DictReader(response.text.splitlines())
    items = list(reader)

    # Группируем по категориям
    categories = {}
    for item in items:
        cat = item.get('category', 'Разное')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    nav_html = ""
    sections_food_html = ""
    sections_bar_html = ""
    flat_items_for_js = []
    global_idx = 0

    for cat_name, cat_items in categories.items():
        # Определяем вкладку по первому товару в категории
        raw_tab = cat_items[0].get('tab', 'Кухня').strip().lower()
        is_bar = (raw_tab == 'бар')
        
        cat_id = f"cat-{hash(cat_name)}"
        tab_key = "bar" if is_bar else "food"
        
        # Скрываем категории бара при первой загрузке
        display_style = 'style="display: none;"' if is_bar else 'style="display: inline-block;"'
        
        nav_html += f'<a href="#{cat_id}" class="nav-item" data-tab="{tab_key}" {display_style}>{cat_name}</a>'
        
        section_html = f'<h2 id="{cat_id}" class="category-title">{cat_name}</h2>\n<div class="menu-grid">'
        for item in cat_items:
            price_val = item.get('price')
            price_html = f'<div class="product-price">{price_val} ₽</div>' if price_val else ''
            img_src = item.get('img', '')
            
            section_html += f'''
            <div class="product-card" onclick="openModal({global_idx})">
                <img src="{img_src}" class="product-img" loading="lazy">
                <div class="product-info">
                    <div class="product-title">{item['name']}</div>
                    {price_html}
                </div>
            </div>'''
            flat_items_for_js.append(item)
            global_idx += 1
        section_html += '</div>\n'
        
        if is_bar:
            sections_bar_html += section_html
        else:
            sections_food_html += section_html

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    final_html = template.replace('{nav_items}', nav_html)
    final_html = final_html.replace('{sections_food}', sections_food_html)
    final_html = final_html.replace('{sections_bar}', sections_bar_html)
    final_html = final_html.replace('{items_json}', json.dumps(flat_items_for_js, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    build()
