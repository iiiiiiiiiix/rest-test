# Project: Modnyi Lounge Bar Menu (Static Site Generator + PWA and Automatic Sync)

## Обзор проекта
This is a static site generator built with Python (uv). Автоматизированная одностраничная витрина меню лаундж-бара, синхронизируемая с Google Sheets вместо базы данных
- Entry point: `.github/workflows/build.yml`
- **Источник данных:** Google Sheets (CSV экспорт).
- **Сборка:** GitHub Actions (build.yml) запускает Python-скрипты.
- **Frontend:** Статический pre-rendered HTML + Service Worker (PWA).
- **Особенности:** Оффлайн-режим, обработка фото, автогенерация PDF.

## Архитектура и Техстек
Проект использует стек **Python + GitHub Actions + Vanilla JS без зависимостей**.
- **Google Sheets**: Источник данных (меню, цены, граммовка, категории и так далее).
- **process_images.py:** Скачивает фото из Google Sheet таблицы (в виде ссылок на Google Drive), конвертирует фото в WebP (две версии: thumbs и full), в том числе обрабатывает прозрачность и HEIC (Pillow + pillow-heif).
- **build.py:** Генерирует статическую страницу index.html на основе template.html, внедряя в него JSON с данными из таблицы Google Sheets.
- **sw.js:** Кастомный Service Worker с логикой "Network First" для страницы и "Cache First" для ассетов.
- **build_pdf.py:** Генерирует pdf версию меню из данных Google Sheets, используя WeasyPrint
- **build_pdf_full.py:** Генерирует pdf версию с картинками, визуально подобно сайту
- **GitHub Actions**: Запускает пайплайн сборки при обновлении данных (файл .github/workflows/build.yml)
- **оффлайн-режим, фоновая предзагрузка и PWA**: стратегия Network First для HTML и Cache First для медиа. После первой загрузки страницы скрипт в `template.html` скачивает все изображения в Cache Storage.

## Структура папок
- `assets/img/thumbs/`: Оптимизированные превью (600px).
- `assets/img/full/`: Полноразмерные фото (1600px).
- `template.html`: Базовый шаблон сайта.
- `sw.js`: Логика Service Worker.

## Общие правила поведения
- Think step by step in English, then respond in Russian.
- Оффлайн-режим критически важен
- не правь index.html напрямую (потому что HTML генерируется через build.py из template.html)

## Правила кода (Python)
- Используй uv run для запуска скриптов.
- Type hints, PEP 8, минимальные зависимости, последние лучшие практики

## Правила фронтенда
- Современный семантический vanilla HTML
- современный CSS без frameworks
- современный vanilla JS без dependencies
- чистый код HTML/CSS/JS
