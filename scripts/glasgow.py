from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def get_table_data(driver, wait):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-bordered")))
    table = driver.find_element(By.CLASS_NAME, "table-bordered")
    headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
    rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip the header row
    data = []
    
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        row_data = {headers[i]: (cols[i].text if i < len(cols) else 'Glasgow') for i in range(len(headers))}
        row_data['Tag'] = 'Glasgow'
        data.append(row_data)

    return data

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)
    try:
        driver.get('https://www.glasgowstockyards.com/marketreport.php')

        market_reports = get_table_data(driver, wait)

        json_data = json.dumps(market_reports, indent=4)
        print(json_data)

    except Exception as e:
        print(f"An error occurred: {e}")
