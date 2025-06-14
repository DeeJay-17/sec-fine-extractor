import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime

# Configuration
USER_AGENT = "Your Name your.name@example.com"
BASE_URL = "https://www.sec.gov"
SEARCH_URL = f"{BASE_URL}/enforcement-litigation/administrative-proceedings"
OUTPUT_FOLDER = "sec_pdfs"
EXCEL_FILE = "sec_documents.xlsx"
HEADERS = {"User-Agent": USER_AGENT}

def create_output_folder():
    """Create output folder for PDFs if it doesn't exist"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

def download_pdf(url, filename):
    """Download a PDF file and save it locally"""
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def search_sec_proceedings(keyword):
    """Search SEC administrative proceedings and extract document details"""
    # Prepare form data for POST request
    form_data = {
        'populate': keyword,
        'year': 'All',
        'month': 'All'
    }
    
    try:
        # Send POST request with search parameters
        response = requests.post(SEARCH_URL, headers=HEADERS, data=form_data)
        response.raise_for_status()
        
        # Parse HTML response
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the results table
        table = soup.find('table')
        if not table:
            print("No results table found")
            return []
        
        # Extract table rows (skip header row)
        rows = table.find_all('tr')[1:]
        if not rows:
            print("No results found")
            return []
        
        documents = []
        for row in rows:
            try:
                # Extract table cells
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                
                # Extract date
                date_str = cells[0].get_text(strip=True)
                try:
                    release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        release_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
                    except:
                        release_date = date_str
                
                # Extract company name and PDF URL
                company_cell = cells[1]
                company_name = company_cell.get_text(strip=True)
                pdf_link = company_cell.find('a', href=True)
                pdf_url = BASE_URL + pdf_link['href'] if pdf_link and pdf_link['href'].endswith('.pdf') else None
                
                # Extract release number
                release_number = cells[2].get_text(strip=True)
                
                if pdf_url:
                    documents.append({
                        'release_date': release_date,
                        'company_name': company_name,
                        'release_number': release_number,
                        'pdf_url': pdf_url,
                        'local_path': ''
                    })
            except Exception as e:
                print(f"Error processing row: {str(e)}")
        
        return documents
    
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def main():
    # Create output folder
    create_output_folder()
    
    # Get search keyword from user
    keyword = input("Enter company name or keyword to search: ").strip()
    if not keyword:
        print("No keyword provided. Exiting.")
        return
    
    # Search SEC proceedings
    print(f"Searching SEC proceedings for '{keyword}'...")
    documents = search_sec_proceedings(keyword)
    print(f"Found {len(documents)} documents")
    
    # Download PDFs and update local paths
    for doc in documents:
        # Generate filename from company name and date
        clean_name = re.sub(r'[^\w\-_\. ]', '_', doc['company_name'])[:50]
        filename = f"{clean_name}_{doc['release_date']}.pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Download PDF
        print(f"Downloading: {doc['company_name']} - {doc['release_date']}")
        if download_pdf(doc['pdf_url'], pdf_path):
            doc['local_path'] = pdf_path
        time.sleep(1)  # Respectful crawling delay
    
    # Save results to Excel
    if documents:
        df = pd.DataFrame(documents)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Saved {len(documents)} records to {EXCEL_FILE}")
    else:
        print("No documents to save")

if __name__ == "__main__":
    import re
    main()