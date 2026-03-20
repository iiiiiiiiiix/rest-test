import requests
import csv
import os
from weasyprint import HTML

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def get_drive_id(url):
    if not url: return None
    return url.split('/d/')[1].split('/')[0] if '/d/' in url else (url.split('id=')[1].split('&')[0] if 'id=' in url else None)

def build_pdf():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        items = list(csv.DictReader(response.text.splitlines()))
    except Exception as e:
        print(f"Error: {e}"); return

    # Подключаем Inter из Google Fonts для стабильности в Ubuntu
    style = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    :root { --primary: #d66a40; --text: #4a3f35; --accent: #8c7f70; }
    
    @page { size: A4; margin: 15mm; }
    
    body { 
        font-family: 'Inter', sans-serif; 
        color: var(--text); 
        line-height: 1.4; 
        font-size: 11pt; 
    }
    
    .tab-title { 
        font-size: 24pt; color: var(--primary); 
        margin-top: 30pt; border-bottom: 1px solid var(--primary); 
        text-transform: uppercase; letter-spacing: 1px;
    }
    
    .category-title { font-size: 16pt; margin: 20pt 0 10pt; font-weight: 700; }
    
    .product-card { 
        display: flex; margin-bottom: 12pt; border-bottom: 0.5pt solid #eee; 
        padding-bottom: 8pt; page-break-inside: avoid; 
    }
    
    .product-img { width: 60pt; height: 60pt; object-fit: cover; border-radius: 6pt; margin-right: 12pt; }
    
    .product-info { flex: 1; }
    
    .product-header { display: flex; justify-content: space-between; align-items: baseline; }
    
    .product-name { font-weight: 700; font-size: 12pt; }
    
    .product-price { color: var(--primary); font-weight: 800; white-space: nowrap; }
    
    .product-meta { font-size: 9pt; color: var(--accent); margin-top: 2pt; }
    
    .product-desc { font-size: 10pt; opacity: 0.8; margin-top: 4pt; }
    """

    content_html = f'<html><head><meta charset="UTF-8"><style>{style}</style></head><body>'

    # Группировка
    sections = {"Кухня": {}, "Бар": {}}
    for item in items:
        t = item.get('tab', 'Кухня').strip()
        c = item.get('category', 'Разное')
        if t not in sections: sections[t] = {}
        if c not in sections[t]: sections[t][c] = []
        sections[t][c].append(item)

    for tab_name, categories in sections.items():
        content_html += f'<div class="tab-title">{tab_name}</div>'
        for cat_name, cat_items in categories.items():
            content_html += f'<div class="category-title">{cat_name}</div>'
            for item in cat_items:
                img_id = get_drive_id(item.get('img', ''))
                # Используем локальные thumbs, созданные в process_images.py
                img_path = os.path.abspath(f"assets/img/thumbs/{img_id}.webp")
                
                img_tag = f'<img src="file://{img_path}" class="product-img">' if img_id and os.path.exists(img_path) else ''
                
                desc = item.get('desc', '')
                weight = item.get('weight', '')

                content_html += f'''
                <div class="product-card">
                    {img_tag}
                    <div class="product-info">
                        <div class="product-header">
                            <span class="product-name">{item["name"]}</span>
                            <span class="product-price">{item["price"]} ₽</span>
                        </div>
                        <div class="product-meta">{weight}</div>
                        <div class="product-desc">{desc}</div>
                    </div>
                </div>'''
    
    content_html += '</body></html>'
    
    # Генерация PDF напрямую через WeasyPrint
    HTML(string=content_html).write_pdf("menu.pdf")
    print("PDF created successfully via WeasyPrint")

if __name__ == "__main__":
    build_pdf()