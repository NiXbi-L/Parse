from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import json
import asyncio
import sys
from PlaywrightFunc import get_html
import os

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
save_task = []

async def download_pdf(url):
    try:
        save_path = url.split('/')[-1]
        # Отправляем GET-запрос на указанный URL
        response = requests.get(url.replace(' ', '%20'), stream=True)

        # Проверяем, что запрос успешен (статус код 200)
        if response.status_code == 200:
            # Открываем файл для записи в бинарном режиме
            with open(f'pdf/{save_path}', 'wb') as file:
                # Записываем содержимое ответа в файл
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"PDF успешно скачан и сохранён по пути: pdf/{save_path}")
        else:
            print(f"Ошибка при скачивании: Код статуса {response.status_code}")
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")


async def create_folders():
    # Список папок, которые нужно создать
    folders = ['jsons', 'pdf']

    for folder in folders:
        # Проверяем, существует ли папка
        if not os.path.exists(folder):
            # Создаем папку, если она не существует
            os.makedirs(folder)
            print(f'Папка "{folder}" успешно создана.')
        else:
            print(f'Папка "{folder}" уже существует.')


async def save_dict_to_json(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Словарь успешно сохранён в файл '{filename}'")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")


async def get_links(content_div, url):
    links = content_div.find_all('a', href=True)

    absolute_links = []
    for link in links:
        href = link['href']

        absolute_url = urljoin(url, href)
        if (str(absolute_url).startswith("https:") or str(absolute_url).startswith("http:")) and not (
                'twitter.com' in str(absolute_url) or 'youtube.com' in str(absolute_url) or 'facebook.com' in str(
            absolute_url)):
            absolute_links.append(absolute_url)

    return absolute_links


async def get_content(url, is_browser=False):
    try:
        if ('.pdf' in url.split("/")[-1]):
            await asyncio.gather(*save_task)
            save = asyncio.create_task(download_pdf(url))
            save_task.append(save)
            return False

        html_code = ''
        if is_browser:
            html_code = await get_html(url)
        else:
            response = requests.get(url)
            response.encoding = response.apparent_encoding
            html_code = response.text
        #print(html_code)

        soup = BeautifulSoup(html_code, 'html5lib')

        paragraph = soup.find_all('p')
        # lists = soup.find_all('li')
        # lis = []
        par = []
        title = soup.find('title')
        if title:
            title = title.get_text(strip=True)

        for i in paragraph:
            par.append(i.get_text(strip=True))

        # for i in lists:
        #     lis.append(i.get_text(strip=True))

        content_list = [par, await get_links(soup, url), title]
        if content_list[0] and content_list[1]:
            return content_list
        else:
            return False

    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
        print(url)
        return False


async def appendChild(i):
    content_list = await get_content(i)
    if not (content_list):
        content_list = await get_content(i, True)
    if content_list:
        lk = {
            "title": content_list[2],
            "publish_time": None,
            "source_url": i,
            "Content": list(set(content_list[0])),
            "links": content_list[1],
            "Child elements": []
        }

        lk2 = {
            "title": lk["title"],
            "publish_time": None,
            "source_url": i,
            "Content": lk["Content"],
        }

        link["Child elements"].append(lk)
        result.append(lk2)


async def appendChild2(j, append_dict, name):
    content_list = await get_content(j)
    if not (content_list):
        content_list = await get_content(j, True)
    if content_list:
        lk = {
            "title": content_list[2],
            "publish_time": None,
            "source_url": j,
            "Content": list(set(content_list[0])),
            "links": content_list[1],
            "Child elements": []
        }

        lk2 = {
            "title": lk["title"],
            "publish_time": None,
            "source_url": j,
            "Content": lk["Content"],
        }

        append_dict["Child elements"].append(lk)
        link["Child elements"].append(append_dict)
        result.append(lk2)
    await save_dict_to_json(result, f"{name}.json")


async def main():
    await create_folders()
    if len(sys.argv) < 3:
        print("Ошибка: Укажите 2 агрумента. 1 - это url 2 - это имя сохраняемого файла")
        sys.exit(1)

    url = sys.argv[1]
    content_list = await get_content(url)
    if not(content_list):
        content_list = await get_content(url, True)
    tasks = []
    if content_list:
        link["source_url"] = url
        link["Content"] = list(set(content_list[0]))
        link["links"] = content_list[1]
        link["title"] = content_list[2]
        link2["Content"] = link["Content"]
        link2["source_url"] = link["source_url"]
        link2["title"] = link["title"]
        result.append(link2)

    for i in link["links"]:
        print(f'current link: {i}')
        task = asyncio.create_task(appendChild(i))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for i in link["Child elements"]:
        for j in i['links']:
            print(f'current link: {j} in {i["source_url"]}')
            task = asyncio.create_task(appendChild2(j, i, f'jsons/{sys.argv[2]}'))
    await save_dict_to_json(result, f'jsons/{sys.argv[2]}.json')


asyncio.run(main())
