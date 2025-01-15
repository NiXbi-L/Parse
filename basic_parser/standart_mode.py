from bs4 import BeautifulSoup
import asyncio
from basic_parser.PlaywrightFunc import get_html
from basic_parser.Anti_bot import anti_bot_get_html
from common_functions.сommon_functions import *
from random import choice
import aiohttp

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


async def tick_saver(args):
    while True:
        await save_dict_to_json(result, f"jsons/{args['file_name']}.json")
        await asyncio.sleep(int(args["saving_period"]))


async def get_content(url, is_browser=False, proxy=None, anti_bot=False):
    try:
        if ('.pdf' in url.split("/")[-1]):
            await asyncio.gather(*save_task)
            save = asyncio.create_task(download_pdf(url))
            save_task.append(save)
            return False
        if not (proxy is None):
            if proxy['is_auth']:
                proxy = f'https://{proxy["login"]}:{proxy["password"]}@{proxy["address"]}:{proxy["port"]}'
            else:
                proxy = f'https://{proxy["address"]}:{proxy["port"]}'

        if is_browser:
            if anti_bot:
                html_code = await anti_bot_get_html(url, proxy=proxy)
            else:
                html_code = await get_html(url, proxy=proxy)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html_code = await response.text()

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
        if content_list[0] or content_list[1]:
            return content_list
        else:
            return False

    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
        print(url)
        return False


async def choise_Base_or_Dynamic_load(url, args, proxy=None):
    content_list = None

    if (args["load_type"] == "auto" or args["load_type"] == "request"):
        content_list = await get_content(url, proxy=proxy)
    if not (content_list) and (args["load_type"] == "auto" or args["load_type"] == "browser"):
        if args['anti_bot'] == 'True':
            content_list = await get_content(url, is_browser=True, anti_bot=True, proxy=proxy)
        else:
            content_list = await get_content(url, True, proxy=proxy)
    return content_list


async def appendChild(url, args, append_dict=None):
    content_list = await choise_Base_or_Dynamic_load(url, args)

    if content_list:
        lk = {
            "title": content_list[2],
            "publish_time": None,
            "source_url": url,
            "Content": list(set(content_list[0])),
            "links": list(set(content_list[1])),
            "Child elements": []
        }

        lk2 = {
            "title": lk["title"],
            "publish_time": None,
            "source_url": url,
            "Content": lk["Content"],
        }

        if append_dict is None:
            link["Child elements"].append(lk)
        else:
            append_dict["Child elements"].append(lk)
            link["Child elements"].append(append_dict)

        result.append(lk2)


async def start_standart(url, args):
    TickSvaerTask = asyncio.create_task(tick_saver(args))

    Links = [url]

    if args["proxy"] == "True":
        proxy_pool = load_proxies()
        content_list = await choise_Base_or_Dynamic_load(url, args, proxy=choice(proxy_pool))
    else:
        content_list = await choise_Base_or_Dynamic_load(url, args)

    chunk_size = int(args["chunk_size"])

    if args['depth'] == "2" or args['depth'] == "3":
        if content_list:
            link["source_url"] = url
            link["Content"] = list(set(content_list[0]))
            link["links"] = list(set(content_list[1]))
            link["title"] = content_list[2]
            link2["Content"] = link["Content"]
            link2["source_url"] = link["source_url"]
            link2["title"] = link["title"]
            result.append(link2)

        links = link["links"]
        for i in range(0, len(links), chunk_size):
            chunk = links[i:i + chunk_size]
            tasks = []
            for link_url in chunk:
                print(f'current link: {link_url}')
                if not (link_url in Links):
                    task = asyncio.create_task(appendChild(link_url, args=args))
                    tasks.append(task)
                    Links.append(link_url)
            await asyncio.gather(*tasks)

    if args["depth"] == "3":
        for i in link["Child elements"]:
            links = i["links"]
            for j in range(0, len(links), chunk_size):
                chunk = links[j:j + chunk_size]
                tasks = []
                for link_url in chunk:
                    print(f'current link: {link_url} in {i["source_url"]}')
                    if not (link_url in Links):
                        task = asyncio.create_task(appendChild(link_url, args, i))
                        tasks.append(task)
                        Links.append(link_url)
                await asyncio.gather(*tasks)

    TickSvaerTask.cancel()
    await save_dict_to_json(result, f"jsons/{args['file_name']}.json")
