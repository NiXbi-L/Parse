import json
from urllib.parse import urljoin
import requests
import os
import aiofiles


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


async def create_folders(folders=None):
    if folders is None:
        folders = ['jsons', 'pdf', 'links']
    else:
        folders.append('jsons')
        folders.append('pdf')
        folders.append('links')

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

async def read_url_pool(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл '{file_path}' не найден.")

        with open(file_path, 'r', encoding='utf-8') as file:
            links = [line.strip() for line in file if line.strip()]

        if not links:
            raise ValueError(f"Файл '{file_path}' пустой.")

        return links

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


def load_proxies():
    proxies = []

    try:
        with open('proxy_pool.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) < 2:
                    print(f"Ошибка: некорректный формат строки: {line}")
                    continue

                is_auth = parts[0] == "A"

                proxy_url = parts[1]
                if not proxy_url.startswith("https://"):
                    print(f"Ошибка: некорректный URL прокси: {proxy_url}")
                    continue

                proxy_address_port = proxy_url.replace("https://", "")
                if ":" not in proxy_address_port:
                    print(f"Ошибка: некорректный формат адреса и порта: {proxy_address_port}")
                    continue

                address, port = proxy_address_port.split(":")
                port = int(port)

                proxy = {
                    "is_auth": is_auth,
                    "address": address,
                    "port": port
                }

                if is_auth:
                    if len(parts) >= 4:
                        proxy["login"] = parts[2]
                        proxy["password"] = parts[3]
                    else:
                        print(f"Ошибка: для прокси с авторизацией не указаны логин и пароль: {line}")
                        continue

                proxies.append(proxy)

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return proxies