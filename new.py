import requests

# URL и данные для POST-запроса
url = "https://xwqy.gsxt.gov.cn/mirco/info_detail"
data = {
    "organId": "52"  # Пример параметра, который может быть нужен
}

# Заголовки, которые браузер отправляет
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "xwqy.gsxt.gov.cn",
    "Origin": "https://xwqy.gsxt.gov.cn",
    "Referer": "https://xwqy.gsxt.gov.cn/mirco/dfj_indep_info_list?organId=52",
    "Sec-Ch-Ua": '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36"
}

# Куки, которые браузер отправляет
cookies = {
    "__jsluid_s": "2fcf949e84950bd076fb84a0d4417a46",
    "__jsluid_h": "88f80e490b115e1d315a10781f329c2d",
    "JSESSIONID": "026CB9A8B4AE9BB02D7F46F86B7CCB49"
}

# Отправка POST-запроса
response = requests.post(url, headers=headers, cookies=cookies, data=data)

# Вывод результата
print(response.status_code)
print(response.text)