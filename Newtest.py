from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import json
import asyncio

link = {
    "this link": "",
    "Content": [],
    "links": [],
    "Child elements": []
}
import sys


async def download_pdf(url):
    """
    Скачивает PDF-файл по указанной ссылке и сохраняет его на диск.

    :param url: Ссылка на PDF-файл.
    :param save_path: Путь для сохранения файла (включая имя файла).
    """
    try:
        save_path = url.split('/')[-1]
        # Отправляем GET-запрос на указанный URL
        response = requests.get(url.replace(' ', '%20'), stream=True)

        # Проверяем, что запрос успешен (статус код 200)
        if response.status_code == 200:
            # Открываем файл для записи в бинарном режиме
            with open(save_path, 'wb') as file:
                # Записываем содержимое ответа в файл
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"PDF успешно скачан и сохранён по пути: {save_path}")
        else:
            print(f"Ошибка при скачивании: Код статуса {response.status_code}")
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")


async def save_dict_to_json(data, filename):
    try:
        # Открываем файл для записи
        with open(filename, 'w', encoding='utf-8') as file:
            # Преобразуем словарь в JSON и записываем в файл
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


async def get_content(url):
    try:
        if ('.pdf' in url.split("/")[-1]):
            await download_pdf(url)
            return False

        response = requests.get(url)
        response.encoding = response.apparent_encoding
        html_code = response.text

        soup = BeautifulSoup(html_code, 'html5lib')

        paragraph = soup.find_all('p')
        lists = soup.find_all('li')
        lis = []
        par = []
        for i in paragraph:
            par.append(i.get_text(strip=True))

        for i in lists:
            lis.append(i.get_text(strip=True))
        return [par + lis, await get_links(soup, url)]


    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
        print(url)
        return False


async def appendChild(i):
    content_list = await get_content(i)
    if content_list:
        lk = {
            "this link": i,
            "Content": [],
            "links": [],
            "Child elements": []
        }

        lk["Content"] = list(set(content_list[0]))
        lk["links"] = content_list[1]
        link["Child elements"].append(lk)


async def appendChild2(j, append_dict, name):
    content_list = await get_content(j)
    if content_list:
        lk = {
            "this link": j,
            "Content": [],
            "links": [],
            "Child elements": []
        }

        lk["Content"] = list(set(content_list[0]))
        lk["links"] = content_list[1]
        append_dict["Child elements"].append(lk)
        link["Child elements"].append(append_dict)

    await save_dict_to_json(link, f"{name}.json")


async def main():
    if len(sys.argv) < 3:
        print("Ошибка: Укажите 2 агрумента. 1 - это url 2 - это имя сохраняемого файла")
        sys.exit(1)

    url = sys.argv[1]
    content_list = await get_content(url)
    tasks = []
    if content_list:
        link["this link"] = url
        link["Content"] = list(set(content_list[0]))
        link["links"] = content_list[1]

    for i in link["links"]:
        print(f'curent link: {i}')
        task = asyncio.create_task(appendChild(i))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for i in link["Child elements"]:
        for j in i['links']:
            print(f'curent link: {j} in {i["this link"]}')
            task = asyncio.create_task(appendChild2(j, i, sys.argv[2]))


asyncio.run(main())
