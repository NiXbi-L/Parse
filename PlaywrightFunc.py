from playwright.async_api import async_playwright

async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe')
        page = await browser.new_page()
        browser = await p.chromium.launch(headless=True)
        # Создаем новую страницу (используем await)
        page = await browser.new_page()

        # Переходим по URL (используем await)
        await page.goto(url)

        # Ждём, пока страница загрузится (используем await)
        await page.wait_for_timeout(5000)  # Увеличьте время, если страница загружается долго

        # Получаем HTML после выполнения JavaScript (используем await)
        html = await page.content()

        # Закрываем браузер (используем await)
        await browser.close()

        return html