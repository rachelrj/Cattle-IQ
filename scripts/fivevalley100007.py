from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data
from helpers.conversions import convert_entry
from helpers.clickhouse import insert_batches

def scrape_latest_link(driver, wait):
    driver.get("https://fivevalleyslivestock.com/RepresentativeSales/tabid/7044/Default.aspx")
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/Articles/tabid/7008/ID/']")))
    latest_link = elements[0].get_attribute('href') if elements else None
    return latest_link

def extract_date_from_link(link):
    match = re.search(r'(Representative-Sales--|Representative-Sale--).*?(\w+-\d{1,2}-\d{4})', link)
    if match:
        date_str = match.group(2).replace('-', ' ')
        try:
            return datetime.strptime(date_str, '%B %d %Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Date format error for URL: {link}")
            return None
    return None

def scrape_table_data(driver, link):
    driver.get(link)
    date = extract_date_from_link(link)
    data_list = []
    converted_array_of_arrays = []
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        converted_array_of_arrays = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = {f"Column{index+1}": cell.text.strip() for index, cell in enumerate(cells)}
            row_data['Date'] = date
            row_data['Auction'] = "FiveValley"
            data_list.append(row_data)

            converted_row = None
            try:
                if (row_data['Column4'] and row_data['Column7'] and row_data['Column2'] and row_data['Column5'] and row_data['Column6']):
                    converted_row = convert_entry(
                        date, 
                        "Five Valleys", 
                        "MT", 
                        "Five Valleys",
                        "Auction",
                        row_data['Column4'],
                        100007,
                        row_data['Column7'],
                        row_data['Column2'],
                        row_data['Column5'],
                        row_data['Column6'],
                        None,
                        None,
                        None,
                        None,
                        None,
                        row_data['Column3'] if row_data['Column3'] else None)
                    if converted_row and len(converted_row):
                        converted_array_of_arrays.append(converted_row)
            except Exception as e:
                print("Could not convert row for Five Valleys:")
                print(e)
            insert_batches(converted_array_of_arrays, "Five Valleys", date)
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
