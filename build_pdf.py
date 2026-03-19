import requests
import csv
import os
from weasyprint import HTML, CSS

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"
LOGO_URL = "https://raw.githubusercontent.com/iiiiiiiiiix/rest-test/main/assets/logo.svg"

def build_pdf():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        reader = csv.DictReader(response.text.splitlines())
        items = list(reader)

        logo_response = requests.get(LOGO_URL, timeout=15)
        logo_content = logo_response.content if logo_response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return

    tabs = {'Кухня': {}, 'Бар': {}}
    for item in items:
        tab_name = item.get('tab', 'Кухня').strip()
        cat = item.get('category', 'Разное')
        target_tab = 'Бар' if tab_name.lower() == 'бар' else 'Кухня'
        if cat not in tabs[target_tab]:
            tabs[target_tab][cat] = []
        tabs[target_tab][cat].append(item)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 12mm;
                background-color: #F5E6D3;
            }}
            
            body {{
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                color: #1E1E1E;
                margin: 0;
                padding: 0;
            }}

            .header-block {{
                column-span: all;
                text-align: center;
                margin-bottom: 12mm;
            }}

            h1 {{
                text-align: center;
                font-size: 24pt;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-top: 5mm;
                margin-bottom: 10mm;
                color: #1E1E1E;
                column-span: all;
            }}

            .menu-columns {{
                column-count: 2;
                column-gap: 12mm;
                column-fill: balance;
            }}

            .category-block {{
                display: block;
                break-inside: auto;
                margin-bottom: 12mm;
            }}

            .category-title {{
                text-align: center;
                font-size: 15pt;
                text-transform: uppercase;
                margin: 0 0 6mm 0;
                font-weight: normal;
                border-bottom: 1px solid rgba(0,0,0,0.1);
                padding-bottom: 2mm;
                break-after: avoid; /* Запрещаем заголовку категории отрываться от первого блюда */
            }}

            .item {{
                display: flex;
                break-inside: avoid; /* Полный запрет разрыва внутри блюда */
                margin-bottom: 3mm;
                justify-content: space-between;
                align-items: baseline; /* Название и цена на одном уровне (по базовой линии) */
            }}

            .item-content {{
                flex: 1;
                padding-right: 4mm;
            }}

            .item-name {{
                font-weight: bold;
                font-size: 11pt;
                line-height: 1.15;
                display: block;
            }}

            .item-meta {{
                font-size: 8.5pt;
                color: #4a3e35;
                line-height: 1.15;
                opacity: 0.85;
                display: block;
                margin-top: 2px;
            }}

            .item-price-block {{
                display: flex;
                align-items: baseline;
                white-space: nowrap;
                font-weight: bold;
                flex-shrink: 0;
            }}

            .item-weight {{
                font-size: 9pt;
                color: #4a3e35;
                font-weight: normal;
            }}

            .price-divider {{
                font-size: 11pt;
                margin: 0 2px;
                color: #1E1E1E;
            }}

            .item-price {{
                font-size: 11pt;
            }}
        </style>
    </head>
    <body>
    <div class="header-block">{logo_content.decode("utf-8") if logo_content else ""}</div>
    """

    for tab_name, categories in tabs.items():
        if not categories: continue
        
        # Начинаем Бар с новой страницы
        page_break = 'style="page-break-before: always;"' if tab_name == 'Бар' else ''
        
        html_content += f'<div {page_break}>'
        tab_title = '' if tab_name.lower() == 'кухня' else f'<h1>{tab_name}</h1>'
        html_content += tab_title
        html_content += '<div class="menu-columns">'
        
        for cat_name, cat_items in categories.items():
            # Оборачиваем каждую категорию в блок .category-block
            html_content += f'<div class="category-block"><h2 class="category-title">{cat_name}</h2>'
            
            for item in cat_items:
                name = item.get('name', '')
                price = item.get('price', '').strip()
                desc = item.get('desc', '').strip()
                weight = item.get('weight', '').strip()

                price_block = ""
                if weight and price:
                    price_block = f'<span class="item-weight">{weight}</span><span class="price-divider">/</span><span class="item-price">{price} ₽</span>'
                elif price:
                    price_block = f'<span class="item-price">{price} ₽</span>'
                elif weight:
                    price_block = f'<span class="item-weight">{weight}</span>'
                
                html_content += f"""
                <div class="item">
                    <div class="item-content">
                        <span class="item-name">{name}</span>
                        {f'<span class="item-meta">{desc}</span>' if desc else ''}
                    </div>
                    <div class="item-price-block">{price_block}</div>
                </div>
                """
            html_content += '</div>' # Закрываем .category-block

        html_content += '</div></div>'

    html_content += "</body></html>"

    # Сохранить в html виде для дебага в браузере
    # with open('menu_debug.html', 'w', encoding='utf-8') as f:
    #     f.write(html_content)

    print("Генерация PDF...")
    HTML(string=html_content, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf(
        'menu_text.pdf', 
        stylesheets=[CSS(string='svg { width: 140px; height: auto; margin: 0 auto; display: block; }')]
    )
    print("PDF сгенерирован!")

if __name__ == "__main__":
    build_pdf()
