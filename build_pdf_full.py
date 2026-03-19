import requests
import csv
import os

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

def get_drive_id(url):
    if not url: return None
    return url.split('/d/')[1].split('/')[0] if '/d/' in url else (url.split('id=')[1].split('&')[0] if 'id=' in url else None)

def build_pdf_html():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        items = list(csv.DictReader(response.text.splitlines()))
    except Exception as e:
        print(f"Error: {e}"); return

    # Стили для PDF (A4, Print-friendly)
    style = """
    <style>
        :root { --primary: #d66a40; --bg: #ffffff; --text: #4a3f35; --accent: #8c7f70; }
        body { font-family: -apple-system, sans-serif; margin: 0; padding: 20px; color: var(--text); background: #white; }
        .header { text-align: center; margin-bottom: 30px; }
        .header img { width: 150px; }
        .tab-title { font-size: 28px; border-bottom: 2px solid var(--primary); margin: 40px 0 20px; padding-bottom: 10px; color: var(--primary); text-transform: uppercase; letter-spacing: 2px; }
        .category-title { font-size: 20px; margin: 25px 0 15px; color: var(--text); font-weight: bold; }
        .menu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .product-card { display: flex; gap: 12px; break-inside: avoid; border-bottom: 1px solid #eee; padding-bottom: 10px; min-height: 100px; }
        .product-img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
        .product-info { flex-grow: 1; }
        .product-header { display: flex; justify-content: space-between; align-items: flex-start; }
        .product-title { font-weight: 700; font-size: 14px; margin-right: 10px; }
        .product-price { font-weight: 800; color: var(--primary); white-space: nowrap; }
        .product-weight { font-size: 11px; color: var(--accent); margin-top: 2px; }
        .product-desc { font-size: 11px; line-height: 1.3; margin-top: 5px; opacity: 0.8; }
        @media print { .tab-title { break-before: page; } .tab-title:first-of-type { break-before: auto; } }
    </style>
    """

    content_html = f'<html><head><meta charset="UTF-8">{style}</head><body>'
    content_html += '<div class="header"><img src="https://xmgnuvljkvpmksevkwyx.supabase.co/storage/v1/object/public/menu-images/newlogs.svg"></div>'

    # Группировка по Табам (Кухня/Бар), а внутри по Категориям
    tabs = {"Кухня": {}, "Бар": {}}
    for item in items:
        t = item.get('tab', 'Кухня').strip()
        c = item.get('category', 'Разное')
        if t not in tabs: tabs[t] = {}
        if c not in tabs[t]: tabs[t][c] = []
        tabs[t][c].append(item)

    for tab_name, categories in tabs.items():
        content_html += f'<h1 class="tab-title">{tab_name}</h1>'
        for cat_name, cat_items in categories.items():
            content_html += f'<h2 class="category-title">{cat_name}</h2><div class="menu-grid">'
            for item in cat_items:
                img_id = get_drive_id(item.get('img', ''))
                img_path = f"assets/img/thumbs/{img_id}.webp"
                img_tag = f'<img src="{img_path}" class="product-img">' if img_id and os.path.exists(img_path) else '<div style="width:80px"></div>'
                
                desc = item.get('desc', '').strip()
                desc_html = f'<div class="product-desc">{desc}</div>' if desc else ''
                weight = item.get('weight', '').strip()
                weight_html = f'<div class="product-weight">{weight}</div>' if weight else ''

                content_html += f'''
                <div class="product-card">
                    {img_tag}
                    <div class="product-info">
                        <div class="product-header">
                            <span class="product-title">{item["name"]}</span>
                            <span class="product-price">{item["price"]} ₽</span>
                        </div>
                        {weight_html}
                        {desc_html}
                    </div>
                </div>'''
            content_html += '</div>'
    
    content_html += '</body></html>'
    
    with open('menu_pdf_preview.html', 'w', encoding='utf-8') as f:
        f.write(content_html)

if __name__ == "__main__":
    build_pdf_html()
