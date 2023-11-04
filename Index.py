from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
import re
from datetime import datetime

def run_scrape():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')

    service = FirefoxService(log_path=None)
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get('https://www.montanalivestockauction.com/market-reports')
        data = web_scraping_test(driver, wait)
        print(data)
        return data
    except Exception as error:
        return str(error)
    finally:
        driver.quit()

def get_date(driver, wait):
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
            "date": date
        }
        sales.append(info)

def web_scraping_test(driver, wait):
    sales = []

    try:
        date = get_date(driver, wait)

        # Find all buttons with the specified class name and loop through them
        buttons = driver.find_elements(By.XPATH, "//a[@role='tab' and contains(@class, 'nav-link')]")
        for button in buttons:
            type_ = button.text.strip().upper()  # Assuming the type is the button text
            # Each click is wrapped in a try-except block
            try:
                wait.until(EC.element_to_be_clickable(button)).click()
                print(f"Clicked {type_} button")
                
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

if __name__ == "__main__":
    run_scrape()
