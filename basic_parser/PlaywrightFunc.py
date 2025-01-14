from playwright.async_api import async_playwright


async def get_html(url, proxy=None):
    async with async_playwright() as p:
        if proxy:
            proxy_settings = {
                "server": f"http://{proxy['address']}:{proxy['port']}",
            }
            if proxy.get("is_auth"):
                proxy_settings["username"] = proxy["login"]
                proxy_settings["password"] = proxy["password"]
            browser = await p.chromium.launch(proxy=proxy_settings)
        else:
            browser = await p.chromium.launch()

        page = await browser.new_page()

        await page.goto(url)

        await page.wait_for_load_state("networkidle")
        html = await page.content()
        await browser.close()

        return html
