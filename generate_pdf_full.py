import asyncio
from pyppeteer import launch
import os

async def generate_pdf():
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    # Загружаем созданный HTML файл
    path = os.path.abspath("menu_pdf_preview.html")
    await page.goto(f'file://{path}', {'waitUntil': 'networkidle0'})
    
    # Настройки PDF: A4, поля, масштаб
    await page.pdf({
        'path': 'menu.pdf',
        'format': 'A4',
        'printBackground': True,
        'margin': {'top': '20px', 'bottom': '20px', 'left': '20px', 'right': '20px'}
    })
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(generate_pdf())
