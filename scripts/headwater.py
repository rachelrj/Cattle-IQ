import datetime
import fitz  # PyMuPDF
import re
from dateutil.parser import parse
import os
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from helpers.s3 import store_data 

def get_last_monday():
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())

def format_date_for_url(date):
    return date.strftime("%-m-%-d-%y") if os.name != 'nt' else date.strftime("%#m-%#d-%y")

def extract_data_from_pdf_text(pdf_text, date):
    data = []
    current_category = None
    for line in pdf_text.split('\n'):
        if line.strip() == "":
            continue
        if '__' in line:  # Detect category separator
            current_category = line.strip('_ \n')
        else:
            # Replace ', ' with ',' to avoid splitting buyer names that contain a comma
            sanitized_line = line.replace(', ', ',')
            parts = re.split(r'\s{2,}', sanitized_line.strip())
            if len(parts) >= 4:
                # Put the space back after the comma for the buyer name
                parts[0] = parts[0].replace(',', ', ')
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
    monday = get_last_monday()
    formatted_date = format_date_for_url(monday)
    page_url = f"{base_url}{formatted_date}/"
    print(f"Accessing URL: {page_url}")

    try:
        driver.get(page_url)
        wait = WebDriverWait(driver, 10)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        iframe_src = iframe.get_attribute('src')

        if iframe_src:
            print(f"Found iframe source: {iframe_src}")
            # Use requests to download the iframe content
            response = requests.get(iframe_src)
            if response.status_code == 200:
                # Assuming the content is a PDF file
                filename = f"{formatted_date}.pdf"  # You can customize the filename as needed
                file_path = os.path.join(download_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded iframe content to '{file_path}'")
                return formatted_date
            else:
                print(f"Failed to download content from {iframe_src}")
        else:
            print("No iframe source found.")
    except Exception as e:
        print(f"Error processing URL {page_url}: {e}")
        print(traceback.format_exc())

def extract_date_from_filename(filename):
    # Use a regular expression to extract date-like patterns
    match = re.search(r'(\d{1,2})[-.](\d{1,2})[-.](\d{2,4})', filename)
    if match:
        return match.group(0).replace('.', '-')  # Ensure the date is in MM-DD-YY format
    return None

def process_downloaded_pdfs(download_dir, formatted_date):
    all_extracted_data = []  # List to store all extracted data
    target_file = None

    for file in os.listdir(download_dir):
        if file.endswith(".pdf") and formatted_date in file:
            target_file = file
            break

    if target_file:
        file_path = os.path.join(download_dir, target_file)
        try:
            date_str = extract_date_from_filename(target_file)
            if date_str:
                date = parse(date_str, yearfirst=False)  # Parse the date
                formatted_date_str = date.strftime('%Y-%m-%d')  # Convert to YYYY-MM-DD format
                with fitz.open(file_path) as pdf:
                    for page in pdf:
                        page_text = page.get_text("text")
                        extracted_data = extract_data_from_pdf_text(page_text, date.date())
                        all_extracted_data.extend(extracted_data)
            else:
                print(f"Could not extract date from filename {target_file}")
        except Exception as e:
            print(f"Error processing PDF file {target_file}: {e}")
            print(traceback.format_exc())
        finally:
            # Delete the file after use
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    else:
        print(f"No PDF file found for date {formatted_date}.")
    store_data(formatted_date_str, all_extracted_data, "cattleiq/headwater")

def run_scrape(driver):
    download_dir = "/shared-data/"
    base_url = "https://headwaterslivestockauction.com/market-report/hla-"
    formatted_date = find_and_download_pdfs(driver, base_url, download_dir)
    process_downloaded_pdfs(download_dir, formatted_date)
