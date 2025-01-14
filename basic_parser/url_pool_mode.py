from basic_parser.standart_mode import choise_Base_or_Dynamic_load
from common_functions.сommon_functions import read_url_pool, save_dict_to_json, load_proxies
import asyncio
from random import choice

result = []


async def save(url, args):
    if args['proxy'] == "True":
        proxy_pool = load_proxies()
        content_list = await choise_Base_or_Dynamic_load(url, args, choice(proxy_pool))
    else:
        content_list = await choise_Base_or_Dynamic_load(url, args)
    if content_list:
        link = {
            "title": content_list[2],
            "publish_time": None,
            "source_url": url,
            "Content": content_list[0],
            "links": list(set(content_list[1])),
        }
        result.append(link)


async def start_url_pool(args):
    url_pool = await read_url_pool(args['url_pool'])
    tasks = []

    for url in url_pool:
        task = asyncio.create_task(save(url, args))
        tasks.append(task)

    await asyncio.gather(*tasks)
    await save_dict_to_json(result, f'{args["file_name"]}.json')
