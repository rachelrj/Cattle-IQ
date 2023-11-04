import json
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from datetime import datetime, timedelta


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
        for figure in figures:
            table = figure.find_element(By.TAG_NAME, 'table')
            headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip the header row
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = {headers[index]: cell.text for index, cell in enumerate(cells)}
                row_data['auction'] = "sydneylivestock"
                row_data['date'] = date
                data_list.append(row_data)
        return json.dumps(data_list, indent=2)
    except NoSuchElementException:
        print(f"No data available for {date}.")
        return json.dumps([])  # Return an empty list in JSON format if no data was found

def run_scrape(driver):
    past_seven_dates_no_zeros = generate_past_dates()
    all_data = []
    for date in past_seven_dates_no_zeros:
        # Check for a 404 status code using requests
        url = f"https://sidneylivestock.com/{date}/"
        try:
            response = requests.head(url)
            if response.status_code == 404:
                response = requests.get(url)  # Some servers don't respond correctly to HEAD, retry with GET
                if response.status_code == 404:
                    continue
        except requests.RequestException as e:
            print(f"Request exception occurred for {url}: {e}")
            all_data.append({"date": date, "error": str(e), "data": None})
            continue

        try:
            date_data = scrape_data_for_date(date, driver)
            all_data.append(json.loads(date_data))
        except WebDriverException as e:
            print(f"Selenium error occurred while processing {date}: {str(e)}")
            all_data.append({"date": date, "error": str(e), "data": None})
        except Exception as e:  # Catch all other exeptions
            print(f"An error occurred while processing {date}: {str(e)}")
            all_data.append({"date": date, "error": str(e), "data": None}) 
    print(all_data)   