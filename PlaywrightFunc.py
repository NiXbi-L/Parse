from playwright.async_api import async_playwright

async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(url)

        await page.wait_for_timeout(5000)
        html = await page.content()
        await browser.close()

        return html