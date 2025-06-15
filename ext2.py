import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Configuration (remains the same) ---
USER_AGENT = "Your Name your.name@example.com"
SEARCH_URL = "https://www.sec.gov/enforcement-litigation/administrative-proceedings"
OUTPUT_FOLDER = "sec_pdfs"
EXCEL_FILE = "sec_documents.xlsx"

def create_output_folder():
    """Create output folder for PDFs if it doesn't exist."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

def search_sec_proceedings(keyword):
    """Search SEC proceedings using a persistent session to handle cookies."""
    print(f"Searching SEC proceedings for '{keyword}'...")
    
    payload = {
        'keywords': keyword,
        'year': 'All',
        'month': 'All',
        'op': 'Search'
    }
    
    # Use a Session object to persist headers and cookies across requests
    with requests.Session() as session:
        session.headers.update({
            'User-Agent': USER_AGENT
        })

        try:
            # 1. Make a GET request to the search page to establish a session and get cookies.
            print("Establishing session to get necessary cookies...")
            initial_resp = session.get(SEARCH_URL)
            initial_resp.raise_for_status()

            # 2. Now, send the POST request with the search data using the same session.
            print("Sending search query...")
            response = session.post(SEARCH_URL, data=payload, headers={'Referer': SEARCH_URL})
            response.raise_for_status()
            
            # --- DEBUGGING: Save the received HTML to a file ---
            html_filename = f"sec_response_{keyword.replace(' ', '_')}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved raw HTML response to '{html_filename}' for review.")
            # ----------------------------------------------------

            soup = BeautifulSoup(response.text, 'html.parser')
            results_table = soup.find("table", class_="views-table")
            
            if not results_table:
                print("\nNo results table found in the HTML. Please inspect the saved .html file.")
                return []
                
            documents = []
            for row in results_table.find('tbody').find_all('tr'):
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue

                date_str = cells[0].get_text(strip=True)
                try:
                    release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    release_date = date_str

                company_cell = cells[1]
                company_name = company_cell.get_text(strip=True)
                pdf_link = company_cell.find('a')
                
                if not pdf_link or 'href' not in pdf_link.attrs:
                    continue

                pdf_url = f"https://www.sec.gov{pdf_link['href']}"

                release_number = cells[2].get_text(strip=True)

                if pdf_url.endswith('.pdf'):
                    documents.append({
                        'release_date': release_date,
                        'company_name': company_name,
                        'release_number': release_number,
                        'pdf_url': pdf_url,
                        'local_path': ''
                    })
                    
            return documents

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the web request: {e}")
            return []

def download_pdf(url, filename):
    """Download a PDF file using requests."""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def main():
    """Main execution function."""
    create_output_folder()
    
    keyword = input("Enter company name or keyword to search: ").strip()
    if not keyword:
        print("No keyword provided. Exiting.")
        return
        
    documents = search_sec_proceedings(keyword)
    print(f"\nFound {len(documents)} documents.")
    
    if documents:
        for doc in documents:
            clean_name = ''.join(c for c in doc['company_name'] if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{clean_name.replace(' ', '_')}_{doc['release_date']}.pdf"
            pdf_path = os.path.join(OUTPUT_FOLDER, filename)
            
            print(f"Downloading: {doc['company_name']} ({doc['release_date']})")
            if download_pdf(doc['pdf_url'], pdf_path):
                doc['local_path'] = pdf_path
            time.sleep(1)
        
        df = pd.DataFrame(documents)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"\nSaved {len(documents)} records to {EXCEL_FILE}")
    else:
        print("No documents to save.")

if __name__ == "__main__":
    main()