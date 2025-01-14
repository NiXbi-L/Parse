import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import random
import logging
from common_functions.сommon_functions import load_proxies
from random import choice
from dynamic_parser.Silenium_func import wait_for_page_load, wait_for_element

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def anti_bot_get_html(url, proxy=None):
    selector = 'a'
    by = By.TAG_NAME
    max_clicks = 0

    driver = None
    try:
        chrome_options = uc.ChromeOptions()
        chrome_options.binary_location = "chrome-win64/chrome.exe"
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")

        if not (proxy is None):
            if proxy['is_auth']:
                proxy = proxy.split(' ')
                chrome_options.add_argument(f"--proxy-server={proxy['address']}:{proxy['port']}")
                chrome_options.add_argument(f"--proxy-auth={proxy['login']}:{proxy['password']}")
            else:
                chrome_options.add_argument(f"--proxy-server={proxy['address']}:{proxy['port']}")

        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f"user-agent={user_agent}")
        logging.info(f"Используемый User-Agent: {user_agent}")

        logging.info("Запуск браузера...")
        driver = uc.Chrome(options=chrome_options)

        logging.info(f"Переход на страницу: {url}")
        driver.get(url)

        wait_for_page_load(driver)
        wait_for_element(driver, selector, by)

        elements = driver.find_elements(by, selector)
        url_results = []

        elements = elements[:max_clicks]
        html_code = driver.page_source
        for i in range(len(elements)):
            logging.info(f"Переход на страницу: {url}")
            driver.get(url)
            wait_for_page_load(driver)
            wait_for_element(driver, selector, by)

            elements = driver.find_elements(by, selector)
            if i >= len(elements):
                logging.warning(f"Элемент {i + 1} не найден, пропуск.")
                continue

            element = elements[i]

            if not element.is_displayed() or not element.is_enabled():
                logging.warning(f"Элемент {i + 1} не кликабелен, пропуск.")
                continue

            logging.info(f"Клик на элемент {i + 1} из {len(elements)}")

            # Прокрутка страницы до элемента, чтобы он был виден
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
            time.sleep(random.uniform(1, 2))

            # Сохраняем текущую вкладку
            original_window = driver.current_window_handle

            try:
                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                logging.warning(f"Не удалось выполнить клик на элемент {i + 1}: {e}")
                continue

            # Ожидание изменения количества вкладок
            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                new_window = [window for window in driver.window_handles if window != original_window][0]
                driver.switch_to.window(new_window)

                wait_for_page_load(driver)

                html = driver.page_source
                if not html.strip():
                    logging.warning("Новая вкладка пуста.")
                else:
                    file_name = f"page_{i + 1}.html"
                    url_results.append(driver.current_url)

                driver.close()

                driver.switch_to.window(original_window)
            except:
                logging.info("Новая вкладка не открылась, работаем с текущей вкладкой.")
                wait_for_page_load(driver)
                html = driver.page_source
                if not html.strip():
                    logging.warning("Текущая вкладка пуста.")
                else:
                    file_name = f"page_{i + 1}.html"
                    url_results.append(driver.current_url)

                logging.info(f"Возврат на корневую страницу: {url}")
                driver.get(url)
                wait_for_page_load(driver)

            if i < len(elements) - 1:
                delay = random.uniform(5, 10)
                logging.info(f"Ожидание {delay:.1f} секунд...")
                time.sleep(delay)

        return html_code

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return []

    finally:
        if driver:
            logging.info("Закрытие браузера...")
            driver.quit()
