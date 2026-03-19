import requests
import csv
import os
from fpdf import FPDF

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"

class MenuPDF(FPDF):
    def header(self):
        # Оранжевая плашка сверху для стиля
        self.set_fill_color(214, 106, 64)
        self.rect(0, 0, 210, 10, 'F')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def get_drive_id(url):
    if not url: return None
    if '/d/' in url: return url.split('/d/')[1].split('/')[0]
    if 'id=' in url: return url.split('id=')[1].split('&')[0]
    return None

def build_pdf():
    try:
        res = requests.get(SHEET_CSV_URL)
        res.encoding = 'utf-8'
        items = list(csv.DictReader(res.text.splitlines()))
    except Exception as e:
        print(f"Error fetching data: {e}"); return

    pdf = MenuPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Регистрация стандартного шрифта (или системного)
    pdf.set_font("helvetica", size=12)

    sections = {"Кухня": {}, "Бар": {}}
    for item in items:
        t = item.get('tab', 'Кухня').strip()
        c = item.get('category', 'Разное')
        if t not in sections: sections[t] = {}
        if c not in sections[t]: sections[t][c] = []
        sections[t][c].append(item)

    for tab_name, categories in sections.items():
        # Большой заголовок раздела
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(214, 106, 64)
        pdf.cell(0, 20, tab_name.upper(), ln=True, align="L")
        
        for cat_name, cat_items in categories.items():
            # Заголовок категории
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(74, 63, 53)
            pdf.cell(0, 12, cat_name, ln=True)
            pdf.set_draw_color(224, 218, 207) # --accent
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(5)

            for item in cat_items:
                # Начало блока товара
                start_y = pdf.get_y()
                
                # Проверка на наличие картинки
                img_id = get_drive_id(item.get('img', ''))
                img_path = f"assets/img/thumbs/{img_id}.webp"
                
                text_offset = 10
                if img_id and os.path.exists(img_path):
                    # Рисуем картинку (30x30 мм)
                    try:
                        pdf.image(img_path, x=10, y=start_y, w=25, h=25)
                        text_offset = 40 # Сдвигаем текст, если есть фото
                    except:
                        text_offset = 10

                # Название и цена
                pdf.set_xy(text_offset, start_y)
                pdf.set_font("helvetica", "B", 11)
                pdf.set_text_color(74, 63, 53)
                
                # Короткое название, чтобы цена не налезла
                pdf.cell(120, 6, item['name'])
                
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(214, 106, 64)
                pdf.cell(0, 6, f"{item['price']} p.", ln=True, align="R")

                # Вес и Описание
                pdf.set_x(text_offset)
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(140, 127, 112)
                
                info_text = f"({item['weight']}) " if item.get('weight') else ""
                if item.get('desc'):
                    info_text += item['desc']
                
                if info_text:
                    pdf.multi_cell(0, 5, info_text)
                
                # Отступ после товара (минимум высота картинки)
                curr_y = pdf.get_y()
                next_y = max(curr_y, start_y + 28)
                pdf.set_y(next_y)
                pdf.ln(4)

    pdf.output("menu_full.pdf")
    print("PDF with images generated!")

if __name__ == "__main__":
    build_pdf()
