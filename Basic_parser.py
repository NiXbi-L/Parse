from common_functions.сommon_functions import create_folders, read_url_pool
from basic_parser.standart_mode import start_standart
from basic_parser.url_pool_mode import start_url_pool
import asyncio
import sys


async def parse_arg(args):
    res = {
        "load_type": "auto",  # request browser
        "file_name": "output",
        "mode": "standart",  # url_pool
        "url_pool": "links.txt",
        "saving_period": "1",
        "chunk_size": "10",
        "proxy": "False",
        "anti_bot": "False",
        "url": None,
        "referer": None,
        "depth": "3"

    }
    for arg in args:
        arg = arg.split("=")
        res[arg[0]] = arg[1]
    return res


async def main():
    await create_folders()

    if len(sys.argv) < 3:
        print("Ошибка: Нет обязательного аргумента url")
        sys.exit(1)

    args = await parse_arg(sys.argv[1::])
    url = args['url']
    print(args)
    if args["mode"] == "standart":
        if not (url is None):
            await start_standart(url, args)
        else:
            print('Отсутствует параметр url')
    elif args["mode"] == "url_pool":
        await start_url_pool(args)


asyncio.run(main())
