import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
from selenium.webdriver.remote.remote_connection import RemoteConnection

RemoteConnection.set_timeout(10) 

# Function to generate dates for the last seven days
def generate_past_dates(days=7, date_format="%m-%d-%Y"):
    base_date = datetime.now()
    # Use list comprehension to generate past dates without leading zeros
    past_dates = [(base_date - timedelta(days=i)).strftime(date_format) for i in range(days)]
    # Remove leading zeros by splitting the date and reformatting it
    past_dates_no_zeros = ['-'.join(str(int(part)) for part in date.split('-')) for date in past_dates]
    return past_dates_no_zeros

# Example usage
past_seven_dates_no_zeros = generate_past_dates()
print(past_seven_dates_no_zeros)  # Prints dates without leading zeros

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')

hub_url = "http://localhost:4444/wd/hub"

response = requests.head(hub_url, timeout=10)  # set a timeout of 10 seconds

# Try initializing the driver outside of the loop to reuse if necessary
try:
    driver = webdriver.Remote(command_executor=hub_url, options=options)
except WebDriverException as e:
    print(f"Could not initialize the web driver: {e}")
    driver = None  # If driver setup fails, set it to None

# Function to scrape data for a given date and return it in JSON format
def scrape_data_for_date(date, driver):
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
                data_list.append(row_data)
        return json.dumps(data_list, indent=2)
    except NoSuchElementException:
        print(f"No data available for {date}.")
        return json.dumps([])  # Return an empty list in JSON format if no data was found

past_seven_dates = generate_past_dates()

all_data = []
for date in past_seven_dates:
    # Check for a 404 status code using requests
    url = f"https://sidneylivestock.com/{date}/"
    try:
        response = requests.head(url)
        if response.status_code == 404:
            response = requests.get(url)  # Some servers don't respond correctly to HEAD, retry with GET
            if response.status_code == 404:
                print(f"{url} returned 404 Not Found.")
                all_data.append({"date": date, "error": "404 Not Found", "data": None})
                continue
    except requests.RequestException as e:
        print(f"Request exception occurred for {url}: {e}")
        all_data.append({"date": date, "error": str(e), "data": None})
        continue

    if driver:  # Only proceed if the driver was successfully initialized
        # If no 404 status, use Selenium to scrape the page content
        try:
            wait = WebDriverWait(driver, 10)  # Create a new wait instance for each date
            date_data = scrape_data_for_date(date, driver)
            all_data.append(json.loads(date_data))
        except WebDriverException as e:
            print(f"Selenium error occurred while processing {date}: {str(e)}")
            all_data.append({"date": date, "error": str(e), "data": None})
        except Exception as e:  # Catch all other exeptions
            print(f"An error occurred while processing {date}: {str(e)}")
            all_data.append({"date": date, "error": str(e), "data": None})

if driver:
    driver.quit()  # Ensure the driver is quit at the end of the script

