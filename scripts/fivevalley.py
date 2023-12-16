from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data

def scrape_latest_link(driver, wait):
    driver.get("https://fivevalleyslivestock.com/RepresentativeSales/tabid/7044/Default.aspx")
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/Articles/tabid/7008/ID/']")))
    latest_link = elements[0].get_attribute('href') if elements else None
    return latest_link

def extract_date_from_link(link):
    match = re.search(r'Representative-Sales--(\w+-\d{1,2}-\d{4})', link)
    if match:
        date_str = match.group(1).replace('-', ' ')
        return datetime.strptime(date_str, '%B %d %Y').strftime('%Y-%m-%d')
    return None

def scrape_table_data(driver, link):
    driver.get(link)
    date = extract_date_from_link(link)
    data_list = []
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = {f"Column{index+1}": cell.text.strip() for index, cell in enumerate(cells)}
            row_data['Date'] = date
            row_data['Auction'] = "FiveValley"
            data_list.append(row_data)
    except Exception as e:
        print(f"Error occurred while scraping data from {link}: {e}")
    return data_list, date

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)

    try:
        latest_link = scrape_latest_link(driver, wait)
        if latest_link:
            data, date = scrape_table_data(driver, latest_link)
            store_data(date, data, "cattleiq/fivevalleyslivestock")
        else:
            print("No new links found.")
    except Exception as error:
        print(str(error))
