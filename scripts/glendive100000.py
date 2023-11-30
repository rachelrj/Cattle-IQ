from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data
from helpers.conversions import convert_entry
from helpers.clickhouse import insert_batches

def parse_type_column(type_str):
    parts = type_str.split()
    quantity = parts[0] if parts else ''
    breed = parts[1] if len(parts) > 1 else ''
    sex_age = '-'.join(parts[2:]) if len(parts) > 2 else ''
    return quantity, breed, sex_age
def parse_price_column(price_str):
    price = re.search(r'(\$\d+(?:\.\d+)?)(?: / (\w+))?', price_str)
    if price:
        price_value = price.group(1)
        price_factor = price.group(2) if price.group(2) else 'Per Head'
    else:
        price_value = ''
        price_factor = 'Per Head'
    return price_value, price_factor

def get_report_data(driver, link):
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.supsystic-tables-wrap")))
    except Exception as e:
        return {"error": f"Failed to load or find table on the page for link {link}: {e}"}

    try:
        date_match = re.search(r'market-report-(\w+)-(\d+)-(\d{4})', link)
        if date_match:
            date_str = f"{date_match.group(3)}-{date_match.group(1)}-{date_match.group(2)}"
            date = datetime.strptime(date_str, '%Y-%b-%d').strftime('%Y-%m-%d')
        else:
            date = 'Unknown Date'
    except ValueError:
        date = 'Invalid Date Format'
    except Exception as e:
        return {"error": f"Failed to parse date from link {link}: {e}"}

    try:
        data = []
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        current_category = None
        table = soup.find('div', class_='supsystic-tables-wrap')
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 1:
                if cells[0].text.strip() and all(not cell.text.strip() for cell in cells[1:]):
                    current_category = cells[0].text.strip()
                elif len(cells) > 1:
                    entry = {
                        "Date": date,
                        "Category": current_category,
                        "Seller": cells[0].text.strip(),
                        "Type": cells[1].text.strip(),
                        "Weight": cells[2].text.strip(),
                        "Price": cells[3].text.strip(),
                        "Auction": "Glendive"
                    }
                    data.append(entry)
    except Exception as e:
        return {"error": f"Failed to process table data for link {link}: {e}"}

    return data, date

def run_scrape(driver):
    wait = WebDriverWait(driver, 10)
    market_reports = []

    try:
        driver.get('http://www.glendivelivestock.com/category/market-reports/')
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.post")))

        first_post_link = driver.find_element(By.CSS_SELECTOR, "article.post:not(#post-218) h1.entry-title a").get_attribute('href')

        report_data, date = get_report_data(driver, first_post_link)
        if "error" in report_data:
            print(report_data["error"])
        else:
            market_reports.extend(report_data)

    except Exception as e:
        print(f"An error occurred during the main scrape: {e}")

    #s3
    store_data(date, market_reports, "cattleiq/glendiveauction")

    #clickhouse
    try:
        array_of_arrays = []
        for row in market_reports:
            quantity, breed, sex_age = parse_type_column(row["Type"])
            price, pf = parse_price_column(row["Price"])
            entry = convert_entry(date, "Glendive", "MT", "Glendive", "Auction", sex_age, 100000, pf, quantity, row["Weight"], price, None, None, None, sex_age, breed, None, None)
            if entry and len(entry):
                array_of_arrays.append(entry)
        insert_batches(array_of_arrays, "Glendive", date)
    except Exception as e:
        print(f"An clickhouse error occurred for Glendive: {e}")
