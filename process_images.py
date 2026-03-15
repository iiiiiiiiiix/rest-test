import os
import requests
import csv
from PIL import Image
from io import BytesIO

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVezxfe40Q-78IQvERF0u42mMOqAMNAmJ-aHJN4Zx9_S99ud7GYZMaENCQBb_hvujpYjb3sT8aITCM/pub?output=csv"
THUMBS_DIR = 'assets/img/thumbs'
FULL_DIR = 'assets/img/full'

def get_drive_id(url):
    """Извлекает ID из разных форматов ссылок Google Drive"""
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    elif 'id=' in url:
        return url.split('id=')[1].split('&')[0]
    return None

def process():
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(FULL_DIR, exist_ok=True)

    response = requests.get(SHEET_CSV_URL)
    response.encoding = 'utf-8'
    reader = csv.DictReader(response.text.splitlines())
    
    for row in reader:
        img_url = row.get('img', '')
        img_id = get_drive_id(img_url)
        
        if not img_id:
            continue

        full_path = f"{FULL_DIR}/{img_id}.webp"
        thumb_path = f"{THUMBS_DIR}/{img_id}.webp"

        # Если файл уже есть, пропускаем
        if os.path.exists(full_path) and os.path.exists(thumb_path):
            continue

        print(f"Загрузка и оптимизация: {img_id}")
        download_url = f'https://drive.google.com/uc?export=download&id={img_id}'
        
        try:
            res = requests.get(download_url)
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content)).convert('RGB')
                
                # Full size (1600px)
                full_img = img.copy()
                full_img.thumbnail((1600, 1600))
                full_img.save(full_path, 'WEBP', quality=80)

                # Thumbnail (600px)
                thumb_img = img.copy()
                thumb_img.thumbnail((600, 600))
                thumb_img.save(thumb_path, 'WEBP', quality=75)
        except Exception as e:
            print(f"Ошибка с ID {img_id}: {e}")

if __name__ == "__main__":
    process()
