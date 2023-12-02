import datetime
import fitz  # PyMuPDF
import re
import json
import os
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback



def get_last_three_mondays():
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=today.weekday())
    return [last_monday - datetime.timedelta(weeks=i) for i in range(3)]

def extract_data_from_pdf_text(pdf_text, date):
    data = []
    current_category = None
    for line in pdf_text.split('\n'):
        if line.strip() == "":
            continue
        if '__' in line:  # Detect category separator
            current_category = line.strip('_ \n')
        else:
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 4:
                data.append({
                    "Auction": "Headwater",
                    "Buyer Name": parts[0],
                    "Amount and Type": parts[1],
                    "ID": parts[2],
                    "Cwt": parts[3],
                    "Category": current_category,
                    "Date": date.strftime("%Y-%m-%d")
                })
    return data


def find_and_download_pdfs(driver, base_url, download_dir):
    for monday in get_last_three_mondays():
        page_url = f"{base_url}{monday.strftime('%m-%d-%y')}/"
        try:
            driver.get(page_url)
            wait = WebDriverWait(driver, 10)
            iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            driver.switch_to.frame(iframe)
            time.sleep(5)
            pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
            for link in pdf_links:
                pdf_url = link.get_attribute('href')
                if pdf_url:
                    driver.get(pdf_url)
                    time.sleep(5)  # Wait for the download to start
            driver.switch_to.default_content()
        except Exception as e:
            print(f"Error processing URL {page_url}: {e}")
            
def process_downloaded_pdfs(download_dir):
    for file in os.listdir(download_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(download_dir, file)
            print(f"Processing file: {file_path}")
            try:
                date_str = file.split('-')[:3]
                date_str = '-'.join(date_str)
                date = datetime.datetime.strptime(date_str, '%m-%d-%y').date()

                with fitz.open(file_path) as pdf:
                    print(f"Opened PDF: {file}")
                    for page in pdf:
                        page_text = page.get_text("text")
                        extracted_data = extract_data_from_pdf_text(page_text, date)
                        if extracted_data:
                            print(json.dumps(extracted_data, indent=4))
                        else:
                            print("No data extracted from page.")
            except Exception as e:
                print(f"Error processing PDF file {file}: {e}")
                traceback.print_exc()
            finally:
                print(f"Deleting file: {file_path}")
                os.remove(file_path)




def run_scrape(driver):
    try:
        download_dir = "/lib"        
        base_url = "https://headwaterslivestockauction.com/market-report/hla-"
        driver = driver(download_dir)
        find_and_download_pdfs(driver, base_url, download_dir)
        process_downloaded_pdfs(download_dir)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


