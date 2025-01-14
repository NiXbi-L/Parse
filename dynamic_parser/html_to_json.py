import os
import json
from bs4 import BeautifulSoup
import asyncio
from common_functions.сommon_functions import *

# Структура для хранения данных
link = {
    "title": "",
    "publish_time": None,
    "source_url": "",
    "Content": [],
    "links": [],
    "Child elements": []
}

link2 = {
    "title": "",
    "publish_time": None,
    "source_url": "",
    "Content": [],
}

result = []

async def save_dict_to_json(data, filename):
    """Асинхронная функция для сохранения данных в JSON-файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def get_content_from_file(file_path):
    """Функция для получения содержимого из HTML-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_code = file.read()

        soup = BeautifulSoup(html_code, 'html5lib')

        paragraph = soup.find_all('p')
        par = []
        title = soup.find('title')
        if title:
            title = title.get_text(strip=True)

        for i in paragraph:
            par.append(i.get_text(strip=True))

        content_list = [par, await get_links(soup, file_path), title]
        if content_list[0] and content_list[1]:
            return content_list
        else:
            return False

    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return False

async def appendChild(file_path, append_dict=None):
    """Функция для добавления дочерних элементов."""
    content_list = await get_content_from_file(file_path)

    if content_list:
        lk = {
            "title": content_list[2],
            "publish_time": None,
            "source_url": file_path,
            "Content": list(set(content_list[0])),

            "Child elements": []
        }

        lk2 = {
            "title": lk["title"],
            "publish_time": None,
            "source_url": file_path,
            "links": content_list[1],
            "Content": lk["Content"],
        }

        if append_dict is None:
            link["Child elements"].append(lk)
        else:
            append_dict["Child elements"].append(lk)
            link["Child elements"].append(append_dict)

        result.append(lk2)

async def html_to_json(html_folder):
    files = [os.path.join(html_folder, f) for f in os.listdir(html_folder) if f.endswith('.html')]

    tasks = []
    for file_path in files:
        print(f'Обработка файла: {file_path}')
        task = asyncio.create_task(appendChild(file_path))
        tasks.append(task)

    await asyncio.gather(*tasks)

    # Сохранение результатов в JSON-файлы
    await save_dict_to_json(result, f"{html_folder}/output.json")

    print("Обработка завершена.")