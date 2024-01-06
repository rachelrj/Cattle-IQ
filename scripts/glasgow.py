from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
from helpers.s3 import store_data

def get_table_data(driver, wait):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-bordered")))
    table = driver.find_element(By.CLASS_NAME, "table-bordered")
    headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
    rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip the header row
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        # get date
        date = None
        try:
            for col in cols:
                text = col.text
                date_match = re.search(r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\s+\d{1,2}(?:th|st|nd|rd),\s+\d{4}', text)
                if (date_match):
                    date_str = date_match.group()
                    # Remove the suffix from the day
                    date_str = re.sub(r'(st|nd|rd|th)', '', date_str)
                    parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                    date = parsed_date.date().isoformat()
            if (not date):
                raise Exception("Could not get date from Glasgow row")
            row_data = {headers[i]: (cols[i].text if i < len(cols) else 'Glasgow') for i in range(len(headers))}
            row_data['Auction'] = 'Glasgow'
            if data.get(date):
                data[date].append(row_data)
            else:
                data[date] = [row_data]
        except Exception as error:
            print(error)        

    return data, date

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)
    try:
        driver.get('https://www.glasgowstockyards.com/marketreport.php')

        market_reports, date = get_table_data(driver, wait)
        store_data(date, market_reports, "cattleiq/glasgow")

    except Exception as e:
        print(f"An error occurred: {e}")
