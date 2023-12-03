import datetime
import fitz  # PyMuPDF
import re
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from urllib.parse import urljoin
import logging
import requests
import os
import datetime
from helpers.s3 import store_data


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_last_monday():
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())

def get_pdf_url(base_url):
    monday = get_last_monday()
    return f"https://headwaterslivestockauction.com/wp-content/uploads/{monday.year}/{monday.month}/{monday.strftime('%m-%d-%y')}-detailed-market-report.pdf"

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
    print(data)
    store_data(date, data, "cattleiq/lewistown")
    return data

def print_pdf_contents(file_path):
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                return page.get_text()
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")

def download_pdf(pdf_url, download_dir):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_content = response.content
        file_name = pdf_url.split('/')[-1]
        file_path = os.path.join(download_dir, file_name)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)
        print(f"Downloaded {file_path}")
        return file_path;
    else:
        print(f"Failed to download {pdf_url}: Status code {response.status_code}")

def run_scrape(driver):
    download_dir = "/shared-data/"
    base_url = "https://headwaterslivestockauction.com/market-report/hla-"
    driver.get(base_url)

    try:
        pdf_url = get_pdf_url(base_url)
        file_path = download_pdf(pdf_url, download_dir)
        pdf_text = print_pdf_contents(file_path)
        extract_data_from_pdf_text(pdf_text, get_last_monday())
    except Exception as e:
        print(f"Error during download: {e}")
