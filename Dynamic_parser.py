from dynamic_parser.Silenium_func import click_elements_sequentially
from dynamic_parser.html_to_json import html_to_json
import sys
import asyncio
from common_functions.сommon_functions import *
from selenium.webdriver.common.by import By
async def save_links_to_file(links, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')  # Записываем каждую ссылку на новой строке


async def parse_arg(args):
    res = {
        "selector": "a",
        "by": By.TAG_NAME,
        "max_clicks": 10,
        "html_to_json": "True",
        "proxy": "False",
        "referer": None
    }
    for arg in args:
        arg = arg.split("=")
        res[arg[0]] = arg[1]
    return res


async def main():
    args = await parse_arg(sys.argv[2::])
    args["html_output_folder"] = sys.argv[1].split('/')[2]
    await create_folders([args["html_output_folder"]])

    links = click_elements_sequentially(sys.argv[1], args)
    await save_links_to_file(list(set(links)), f'links/{args["html_output_folder"]}.txt')

    if args["html_to_json"] == "True":
        await html_to_json(args["html_output_folder"])

asyncio.run(main())
