from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data
from helpers.conversions import convert_entry
from helpers.redshift import store_redshift
from helpers.clickhouse import insert_batches

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)

    try:
        driver.get('https://www.montanalivestockauction.com/market-reports')
        data = web_scraping_test(driver, wait)
        date = get_date(wait)
        store_data(date, data,"cattleiq/montanalivestockauction")
        
    except Exception as error:
        print(str(error))

def get_date(wait):
    section = wait.until(EC.presence_of_element_located((By.ID, "section-content")))
    text = section.text
    date_match = re.search(
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\s+\d{1,2},\s+\d{4}', text)
    if date_match:
        parsed_date = datetime.strptime(date_match.group(), '%B %d, %Y')
        return parsed_date.date().isoformat()
    return None

def add_rows(sales, tbody, type_, date):
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    array_of_arrays = []
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, 'td')
        info = {
            "seller": tds[0].text,
            "head": tds[1].text,
            "kind": tds[2].text,
            "weight": tds[3].text,
            "price": tds[4].text,
            "unit": tds[5].text,
            "type": type_,
            "date": date,
            "auction": "montanalivestock"
        }
        sales.append(info)
        try: 
            entry = convert_entry(
                date,
                "Butte",
                "MT",
                "Montana Livestock Auction",
                "Auction",
                info["kind"],
                100004,
                info["unit"],
                info["head"],
                info["weight"],
                info["price"],
                None,
                None,
                None,
                None,
                info["type"],
                None,
                None
            )
            array_of_arrays.append(entry)
        except Exception as e:
            print(f"An error occurred convering entry from Montana Livestock: {e}")
    if (array_of_arrays and len(array_of_arrays)):
        try:
            insert_batches(array_of_arrays, "Montana Livestock", date)
        except Exception as e:
            print(f"An error sending to clickhouse from Montana Livestock: {e}")        
        
def web_scraping_test(driver, wait):
    sales = []

    try:
        date = get_date(wait)

        # Find all buttons with the specified class name and loop through them
        buttons = driver.find_elements(By.XPATH, "//a[@role='tab' and contains(@class, 'nav-link')]")
        for button in buttons:
            type_ = button.text.strip().upper()  # Assuming the type is the button text
            try:
                wait.until(EC.element_to_be_clickable(button)).click()
                
                # Wait for the corresponding table to load
                # We assume the table ID follows a specific pattern based on the button text
                table_id = type_.lower()
                tab_panel = wait.until(EC.presence_of_element_located((By.ID, table_id)))
                tbody = tab_panel.find_element(By.TAG_NAME, 'tbody')
                add_rows(sales, tbody, type_, date)

            except Exception as e:
                print(f"Error clicking on {type_} button or processing its data:", e)

    except Exception as e:
        print("Error in web_scraping_test:", e)

    return sales
