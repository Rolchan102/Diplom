import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def get_data_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # options.add_argument("--headless")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    s = Service("C:\chromedriver.exe")
    driver = webdriver.Chrome(
        service=s,
        options=options)

    stealth(driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    url = "file:///E:/Pyton/PycharmProjects/Selenium-stealth/price/index.html"
    driver.get(url)
    # Выбрать прайс-лист: Россия
    select = Select(driver.find_element(By.XPATH, '//*[@id="package_select"]'))
    select.select_by_visible_text('Россия')

    # Срок лицензии
    select = Select(driver.find_element(By.XPATH, '//*[@id="period_license"]'))
    select.select_by_visible_text('12')

    # Льгота
    select = Select(driver.find_element(By.XPATH, '//*[@id="discount_type"]'))
    select.select_by_visible_text('Новая лицензия')

    # Количество
    for i in range(5, 6):
        text_input = driver.find_element(By.XPATH, '//*[@id="business_dwdsscp"]')
        # Удалить предыдущий ввод
        text_input.clear()
        text_input.send_keys(i)

    with open("index_selenium.html", "w", encoding='utf-8') as file:
        file.write(driver.page_source)

    time.sleep(5)
    driver.quit()

    with open("index_selenium.html", encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    l_float = soup.find("div", {"id": "basket"}).find_all("div", class_="l-float", limit=1)
    # print(l_float)
    r_float = soup.find("div", {"id": "basket"}).find_all("div", class_="r-float", limit=1)
    # print(r_float)

    for item in l_float:
        try:
            name = item.find("h6", class_="title").string
        except:
            name = "Нет наименования позиции"

    for item in l_float:
        try:
            product_code = item.find("small").string
        except:
            product_code = "Нет кода продукта"

    for price_per_unit in l_float:
        try:
            price_per_unit = price_per_unit.find("span", class_="gray").string
        except:
            price_per_unit = "Нет цены за позицию"

    for total_price in r_float:
        try:
            total_price = total_price.find("span").string
        except:
            total_price = "Нет итоговой цены"

    print(product_code, ",", name, ",", price_per_unit, ",", total_price)

    with open("Dr.web_price.csv", "w", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            [product_code, name, price_per_unit, total_price]
        )


def main():
    get_data_with_selenium("file:///E:/Pyton/PycharmProjects/Selenium-stealth/price/index.html")


if __name__ == '__main__':
    main()
