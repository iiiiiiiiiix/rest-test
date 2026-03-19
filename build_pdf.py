import requests
import csv
import os
from weasyprint import HTML

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def build_pdf():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        reader = csv.DictReader(response.text.splitlines())
        items = list(reader)
    except Exception as e:
        print(f"Ошибка при загрузке таблицы для PDF: {e}")
        return

    # Группируем по вкладкам и категориям
    tabs = {'Кухня': {}, 'Бар': {}}
    for item in items:
        tab_name = item.get('tab', 'Кухня').strip()
        cat = item.get('category', 'Разное')
        
        # Нормализуем название вкладки
        target_tab = 'Бар' if tab_name.lower() == 'бар' else 'Кухня'
        
        if cat not in tabs[target_tab]:
            tabs[target_tab][cat] = []
        tabs[target_tab][cat].append(item)

    # Генерируем HTML для PDF
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm;
                @bottom-center {{
                    content: counter(page);
                    font-size: 10pt;
                    color: #8c7f70;
                }}
            }}
            body {{
                font-family: sans-serif;
                color: #4a3f35;
                background: #faf7f2;
            }}
            h1 {{
                text-align: center;
                color: #d66a40;
                font-size: 28pt;
                margin-bottom: 5mm;
                text-transform: uppercase;
            }}
            .tab-title {{
                text-align: center;
                font-size: 20pt;
                background: #e0dacf;
                padding: 10px;
                border-radius: 8px;
                margin: 15mm 0 10mm 0;
                page-break-after: avoid;
            }}
            .category-title {{
                font-size: 16pt;
                color: #d66a40;
                border-bottom: 2px solid #d66a40;
                padding-bottom: 5px;
                margin-top: 10mm;
                margin-bottom: 5mm;
                page-break-after: avoid;
            }}
            .item {{
                margin-bottom: 6mm;
                page-break-inside: avoid;
            }}
            .item-header {{
                display: flex;
                align-items: baseline;
                width: 100%;
            }}
            .item-name {{
                font-weight: bold;
                font-size: 12pt;
            }}
            .item-dots {{
                flex-grow: 1;
                border-bottom: 1px dotted #8c7f70;
                margin: 0 8px;
            }}
            .item-price {{
                font-weight: bold;
                font-size: 12pt;
                white-space: nowrap;
            }}
            .item-meta {{
                font-size: 10pt;
                color: #666;
                margin-top: 3px;
                line-height: 1.3;
            }}
            .weight-badge {{
                display: inline-block;
                background: #eee8de;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 9pt;
                margin-right: 8px;
                color: #4a3f35;
            }}
        </style>
    </head>
    <body>
        <h1>Меню</h1>
    """

    for tab_name, categories in tabs.items():
        if not categories: continue
        
        # Добавляем разрыв страницы перед Баром, если Кухня уже вывелась
        style = 'style="page-break-before: always;"' if tab_name == 'Бар' else ''
        html_content += f'<div class="tab-title" {style}>{tab_name}</div>'

        for cat_name, cat_items in categories.items():
            html_content += f'<h2 class="category-title">{cat_name}</h2>'
            
            for item in cat_items:
                name = item.get('name', '')
                price = item.get('price', '')
                desc = item.get('desc', '').strip()
                weight = item.get('weight', '').strip()

                weight_html = f'<span class="weight-badge">{weight}</span>' if weight else ''
                desc_html = f'<span>{desc}</span>' if desc else ''
                
                html_content += f"""
                <div class="item">
                    <div class="item-header">
                        <span class="item-name">{name}</span>
                        <span class="item-dots"></span>
                        <span class="item-price">{price} ₽</span>
                    </div>
                    <div class="item-meta">
                        {weight_html} {desc_html}
                    </div>
                </div>
                """

    html_content += "</body></html>"

    # Рендерим PDF. base_url нужен, если вы захотите добавить картинки по относительным путям.
    print("Генерация PDF...")
    HTML(string=html_content, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf('menu.pdf')
    print("PDF успешно сгенерирован: menu.pdf")

if __name__ == "__main__":
    build_pdf()
