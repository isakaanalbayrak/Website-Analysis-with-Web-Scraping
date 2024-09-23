import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time

service = Service(executable_path="chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

sleep_time = 2

url = "https://books.toscrape.com/"
driver.get(url)
time.sleep(sleep_time)

category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

category_elements = driver.find_elements(By.XPATH, category_elements_xpath)

category_urls = [element.get_attribute("href") for element in category_elements]



driver.get(category_urls[0])
time.sleep(sleep_time)

book_elements_xpath = "//div[@class='image_container']//a"

book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
book_urls = [element.get_attribute("href") for element in book_elements]


max_pagination = 3
urls = category_urls[0]
book_urls = []

for i in range(1, max_pagination):
    update_url = urls if i==1 else url.replace("index", f"page-{i}")
    driver.get(update_url)
    book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

    if not book_elements:
        break

    temp_urls = [element.get_attribute("href") for element in book_elements]
    book_urls.extend(temp_urls)



driver.get(book_urls[0])
time.sleep(sleep_time)

content_div = driver.find_elements(By.XPATH, "//div[@class='content']")

inner_html = content_div[0].get_attribute("innerHTML")

soup = BeautifulSoup(inner_html, "html.parser")


name_elem = soup.find("h1")
book_name = name_elem.text


price_elem = soup.find("p", attrs={"class": "price_color"})
book_price = price_elem.text

regex = re.compile("star-rating")
star_elem = soup.find("p", attrs={"class": regex})

book_star_count = star_elem["class"][-1]


desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
book_desc = desc_elem.text

product_info = {}
table_rows = soup.find("table").find_all("tr")
for row in table_rows:
    key = row.find("th").text
    value = row.find("td").text
    product_info[key] = value

######################################################################################################################################################

def initialize_driver():
    """Inıtializes driver with maximized option"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized");
    driver = webdriver.Chrome(options)
    return driver

def get_travel_and_nonfiction_category_urls(driver, url):
    """Gets category urls from given homepage url"""
    driver.get(url)
    time.sleep(sleep_time)

    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    category_urls = [element.get_attribute("href") for element in category_elements]

    return category_urls

def get_book_urls(driver, url):
    """Fets book urls from given page url"""
    max_pagination = 3


    book_urls =[]
    book_elements_xpath = "//div[@class='image_container']//a"

    for i in range(1, max_pagination):
        update_url = url if i==1 else url.replace("index", f"page-{i}")
        driver.get(update_url)
        time.sleep(sleep_time)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)


        # Controller of pagination
        if not book_elements:
            break

        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)

        return book_urls

def get_book_details(driver, url):
    """Gets book data from given book detail page url"""
    driver.get(url)
    time.sleep(sleep_time)
    content_div = driver.find_elements(By.XPATH, "//div[@class='content']")

    inner_html = content_div[0].get_attribute("innerHTML")

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(inner_html, "html.parser")

    name_elem = soup.find("h1")
    book_name = name_elem.text

    price_elem = soup.find("p", attrs={"class": "price_color"})
    book_price = price_elem.text

    import re

    regex = re.compile("^star-rating")
    star_elem = soup.find("p", attrs={"class": regex})
    book_star_count = star_elem["class"][-1]

    desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
    book_desc = desc_elem.text

    product_info = {}
    table_rows = soup.find("table").find_all("tr")
    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value

    return {"book_name": book_name,
            "book_price": book_price,
            "book_star_count": book_star_count,
            "book_desc": book_desc,
            **product_info} # "**" ile unpack yapmazsak {""book_name: "arman", "book_price": "0", {}} formunda çıktı alırız.

######################################################################################################################################################

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

sleep_time = 0.25

def main():
    base_url = "https://books.toscrape.com/"
    driver = initialize_driver()
    category_urls = get_travel_and_nonfiction_category_urls(driver, base_url)

    data = []
    for cat_url in category_urls:
        book_data = get_book_urls(driver, cat_url)
        for book_url in book_urls:
            book_data = get_book_details(driver, book_url)
            book_data["cat_url"] = cat_url
            data.append(book_data)

    import pandas as pd
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 40)
    pd.set_option("display.width", 2000)
    df = pd.DataFrame(data)

    return df

if __name__ == "__main__":
    print("İşlem Başlatıldı")
    df = main()
