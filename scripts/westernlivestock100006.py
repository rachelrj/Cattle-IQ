from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import re
import sys
sys.path.append('../helpers')
from helpers.conversions import convert_entry
from helpers.s3 import store_data
from helpers.clickhouse import insert_batches

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)

    try:
        driver.get('https://westernlivestockmontana.com/market-report')
        web_scraping_logic(driver, wait)
    except Exception as error:
        print(f"An error occurred running Western Livestock: {error}")
        return str(error)

def extract_date_from_header(header_element):
    date_pattern = re.compile(
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\s+\d{1,2},\s+\d{4}');
    date_text = date_pattern.search(header_element.text)
    if date_text:
        return datetime.strptime(date_text.group(), '%B %d, %Y').date().isoformat()
    return None

def get_table_headers(table):
    thead = table.find_element(By.TAG_NAME, 'thead')
    headers = [th.text.replace("\n", " ").replace("<br>", " ").strip() for th in thead.find_elements(By.TAG_NAME, 'th')]
    return headers

def parse_table_data(table, date, report_title):
    headers = get_table_headers(table)
    rows = table.find_elements(By.XPATH, ".//tr[not(contains(@class, 'mktrpt-cat')) and .//td]")  # All data rows, excluding category
    data_list = []
    array_of_arrays = []
    for row in rows:
        # Extracting row data considering possible 'colspan' that affects the cell count
        cells = row.find_elements(By.TAG_NAME, 'td')
        row_data = dict(zip(headers, [cell.text.strip() for cell in cells]))
        row_data['Date'] = date
        row_data['Report Title'] = report_title
        row_data['Auction'] = "westernlivestock"
        data_list.append(row_data)
        try:
            entry = convert_entry(
                date,
                row_data["City"],
                "MT",
                "Western Livestock Auction",
                "Auction",
                row_data["Color"],
                100006,
                row_data["Price"],
                row_data["Head Count"],
                row_data["Avg. Weight"],
                row_data["Price"],
                None,
                row_data["Report Title"],
                None,
                None,
                None,
                None,
                row_data["Seller"]
            )
            if (entry): 
                array_of_arrays.append(entry)
        except Exception as e:
            print(f"An error occurred converting entry from Western Livestock: {e}")
    
    return data_list, array_of_arrays

def web_scraping_logic(driver, wait):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mktrpt")))  # Wait for the table to be present
    tables = driver.find_elements(By.CLASS_NAME, "mktrpt")
    market_data = []
    clickhouse_data = []
    
    for table in tables:
        # Find the preceding sibling <h2> which contains the date and header info
        header = table.find_element(By.XPATH, './preceding-sibling::h2[1]')
        date = extract_date_from_header(header)
        report_title = header.text.strip()
        
        table_data, ch_data = parse_table_data(table, date, report_title)
        market_data.extend(table_data)
        clickhouse_data.extend(ch_data)
        store_data(date, table_data, "cattleiq/westernlivestockauction")
        if ch_data and len(ch_data):
            insert_batches(ch_data, "Western Livestock", date)
