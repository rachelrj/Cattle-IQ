from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import json
import re
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data

def get_report_data(driver, link):
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.tableizer-table")))
    except Exception as e:
        return {"error": f"Failed to load the page or find the table for link {link}: {e}"}
    
    page_source = driver.page_source
    date_regex = r'[A-Za-z]{3} \d{1,2}, \d{4}'
    match = re.findall(date_regex, page_source)[0]

    try:
        converted_date = datetime.strptime(match, '%b %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        print(f"Failed to convert date: {match}")

    try:
        tables = driver.find_elements(By.CSS_SELECTOR, "table.tableizer-table")
        if not tables:
            return {"error": "No tables found on the page"}
        data = []

        for table in tables:
            headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
            rows = table.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) > 0:
                    entry = {headers[i]: cols[i].text for i in range(len(cols))}
                    entry['Date'] = converted_date
                    entry['Auction'] = "lewistown"
                    data.append(entry)
    except Exception as e:
        return {"error": f"Error while processing table data: {e}"}

    return data, converted_date

def run_scrape(driver):
    market_reports = []

    try:
        report_data, date = get_report_data(driver, 'https://www.lewistownlivestock.com/market-reports')
        if 'error' in report_data:
            print(report_data['error'])
        else:
            market_reports.extend(report_data)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    store_data(date, report_data, "cattleiq/lewistown")
