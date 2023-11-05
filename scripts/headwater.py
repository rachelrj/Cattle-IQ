import datetime
import requests
import fitz
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

def get_pdf_url_from_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_embed = soup.find('embed', attrs={'type': 'application/x-google-chrome-pdf'})
        if pdf_embed and 'original-url' in pdf_embed.attrs:
            return pdf_embed.attrs['original-url']
        else:
            return None
    except Exception as e:
        print(f"Error parsing HTML content from {url}: {e}")
        return None

def run_scrape(driver):
    base_url = "https://headwaterslivestockauction.com/market-report/hla-"
    for monday in get_last_three_mondays():
        formatted_date = monday.strftime("%m-%d-%y")
        report_url = f"{base_url}{formatted_date}/"
        
        print(f"Processing data for: {report_url}")
        pdf_url = get_pdf_url_from_webpage(report_url)
        
        if pdf_url:
            try:
                response = requests.get(pdf_url, timeout=10)
                response.raise_for_status()

                with fitz.open(stream=response.content, filetype="pdf") as pdf:
                    for page in pdf:
                        try:
                            page_text = page.get_text("text")
                            extracted_data = extract_data_from_pdf_text(page_text, monday)
                            print(json.dumps(extracted_data, indent=4))
                        except Exception as e:
                            print(f"Error processing page in PDF: {e}")
                break
            except requests.RequestException as e:
                print(f"Error downloading PDF from {pdf_url}: {e}")
            
        else:
            print(f"No PDF found for the report on: {monday.strftime('%Y-%m-%d')}")