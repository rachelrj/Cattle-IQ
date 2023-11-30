import json
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from datetime import datetime, timedelta
import sys
sys.path.append('../helpers')
from helpers.s3 import store_data
from helpers.conversions import convert_entry
from helpers.clickhouse import insert_batches


def generate_past_dates(days=7, date_format="%m-%d-%Y"):
    base_date = datetime.now()
    # Use list comprehension to generate past dates without leading zeros
    past_dates = [(base_date - timedelta(days=i)).strftime(date_format) for i in range(days)]
    # Remove leading zeros by splitting the date and reformatting it
    past_dates_no_zeros = ['-'.join(str(int(part)) for part in date.split('-')) for date in past_dates]
    return past_dates_no_zeros

def scrape_data_for_date(date, driver):
    wait = WebDriverWait(driver, 10)
    url = f"https://sidneylivestock.com/{date}/"
    driver.get(url)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "wp-block-table")))
        data_list = []
        figures = driver.find_elements(By.CLASS_NAME, "wp-block-table")
        array_of_arrays = []
        for figure in figures:
            table = figure.find_element(By.TAG_NAME, 'table')
            headers = [header.text.replace(':', '') for header in table.find_elements(By.TAG_NAME, 'th')]
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip the header row
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = {headers[index]: cell.text for index, cell in enumerate(cells)}
                row_data['auction'] = "sydneylivestock"
                date_object = datetime.strptime(date, "%m-%d-%Y")
                formatted_date = date_object.strftime("%Y-%m-%d")
                row_data['date'] = formatted_date
                data_list.append(row_data)
                try: 
                    entry = convert_entry(
                    date,
                    "Sidney",
                    "MT",
                    "Sidney Livestock Market",
                    "Auction",
                    row_data["Description"],
                    100005,
                    "Hd",
                    row_data["Head"],
                    row_data["AvgWt"],
                    row_data["Bid"],
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                    )
                    array_of_arrays.append(entry)
                except Exception as e:
                    print(f"An error occurred convering entry from Sidney Livestock: {e}")
        return data_list, array_of_arrays
    except NoSuchElementException:
        print(f"No data available for {date}.")
        return []

def run_scrape(driver):
    past_seven_dates_no_zeros = generate_past_dates()
    
    for date in past_seven_dates_no_zeros:
        url = f"https://sidneylivestock.com/{date}/"
        try:
            response = requests.head(url)
            if response.status_code == 404:
                response = requests.get(url)  # Retry with GET if HEAD request fails
                if response.status_code == 404:
                    print(f"No data available for {date}.")
                    continue
        except requests.RequestException as e:
            print(f"Request exception occurred for {url}: {e}")
            continue

        try:
            formatted_date = datetime.strptime(date, "%m-%d-%Y").strftime("%Y-%m-%d")
            date_data, array_of_arrays = scrape_data_for_date(date, driver)
            if date_data:  # Only store data if there is data to store
                store_data(formatted_date, date_data, "cattleiq/sydneylivestockauction")
            else:
                print(f"No data to store for {date}.")
            if array_of_arrays and len(array_of_arrays):
                insert_batches(array_of_arrays, "Sidney", formatted_date)
        except WebDriverException as e:
            print(f"Selenium error occurred while processing {date}: {str(e)}")
        except Exception as e:
            print(f"An error occurred while processing {date}: {str(e)}")

