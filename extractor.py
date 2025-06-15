# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import os
# import time
# from datetime import datetime

# # Configuration
# USER_AGENT = "Your Name your.name@example.com"
# BASE_URL = "https://www.sec.gov"
# SEARCH_URL = f"{BASE_URL}/enforcement-litigation/administrative-proceedings"
# OUTPUT_FOLDER = "sec_pdfs"
# EXCEL_FILE = "sec_documents.xlsx"
# HEADERS = {"User-Agent": USER_AGENT}

# def create_output_folder():
#     """Create output folder for PDFs if it doesn't exist"""
#     if not os.path.exists(OUTPUT_FOLDER):
#         os.makedirs(OUTPUT_FOLDER)

# def download_pdf(url, filename):
#     """Download a PDF file and save it locally"""
#     try:
#         response = requests.get(url, headers=HEADERS, stream=True)
#         response.raise_for_status()
        
#         with open(filename, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         return True
#     except Exception as e:
#         print(f"Error downloading {url}: {str(e)}")
#         return False

# def search_sec_proceedings(keyword):
#     """Search SEC administrative proceedings and extract document details"""
#     # Prepare form data for POST request
#     form_data = {
#         'populate': keyword,
#         'year': 'All',
#         'month': 'All'
#     }
    
#     try:
#         # Send POST request with search parameters
#         response = requests.post(SEARCH_URL, headers=HEADERS, data=form_data)
#         response.raise_for_status()
        
#         # Parse HTML response
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Find the results table
#         table = soup.find('table')
#         if not table:
#             print("No results table found")
#             return []
        
#         # Extract table rows (skip header row)
#         rows = table.find_all('tr')[1:]
#         if not rows:
#             print("No results found")
#             return []
        
#         documents = []
#         for row in rows:
#             try:
#                 # Extract table cells
#                 cells = row.find_all('td')
#                 if len(cells) < 3:
#                     continue
                
#                 # Extract date
#                 date_str = cells[0].get_text(strip=True)
#                 try:
#                     release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
#                 except ValueError:
#                     try:
#                         release_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
#                     except:
#                         release_date = date_str
                
#                 # Extract company name and PDF URL
#                 company_cell = cells[1]
#                 company_name = company_cell.get_text(strip=True)
#                 pdf_link = company_cell.find('a', href=True)
#                 pdf_url = BASE_URL + pdf_link['href'] if pdf_link and pdf_link['href'].endswith('.pdf') else None
                
#                 # Extract release number
#                 release_number = cells[2].get_text(strip=True)
                
#                 if pdf_url:
#                     documents.append({
#                         'release_date': release_date,
#                         'company_name': company_name,
#                         'release_number': release_number,
#                         'pdf_url': pdf_url,
#                         'local_path': ''
#                     })
#             except Exception as e:
#                 print(f"Error processing row: {str(e)}")
        
#         return documents
    
#     except Exception as e:
#         print(f"Search error: {str(e)}")
#         return []

# def main():
#     # Create output folder
#     create_output_folder()
    
#     # Get search keyword from user
#     keyword = input("Enter company name or keyword to search: ").strip()
#     if not keyword:
#         print("No keyword provided. Exiting.")
#         return
    
#     # Search SEC proceedings
#     print(f"Searching SEC proceedings for '{keyword}'...")
#     documents = search_sec_proceedings(keyword)
#     print(f"Found {len(documents)} documents")
    
#     # Download PDFs and update local paths
#     for doc in documents:
#         # Generate filename from company name and date
#         clean_name = re.sub(r'[^\w\-_\. ]', '_', doc['company_name'])[:50]
#         filename = f"{clean_name}_{doc['release_date']}.pdf"
#         pdf_path = os.path.join(OUTPUT_FOLDER, filename)
        
#         # Download PDF
#         print(f"Downloading: {doc['company_name']} - {doc['release_date']}")
#         if download_pdf(doc['pdf_url'], pdf_path):
#             doc['local_path'] = pdf_path
#         time.sleep(1)  # Respectful crawling delay
    
#     # Save results to Excel
#     if documents:
#         df = pd.DataFrame(documents)
#         df.to_excel(EXCEL_FILE, index=False)
#         print(f"Saved {len(documents)} records to {EXCEL_FILE}")
#     else:
#         print("No documents to save")

# if __name__ == "__main__":
#     import re
#     main()



# import os
# import time
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd

# # Configuration
# USER_AGENT = "Your Name your.name@example.com"
# BASE_URL = "https://www.sec.gov"
# SEARCH_URL = f"{BASE_URL}/enforcement-litigation/administrative-proceedings"
# OUTPUT_FOLDER = "sec_pdfs"
# EXCEL_FILE = "sec_documents.xlsx"

# def create_output_folder():
#     """Create output folder for PDFs if it doesn't exist"""
#     if not os.path.exists(OUTPUT_FOLDER):
#         os.makedirs(OUTPUT_FOLDER)

# def setup_selenium():
#     """Configure Selenium WebDriver"""
#     options = webdriver.ChromeOptions()
#     options.add_argument(f'user-agent={USER_AGENT}')
#     options.add_argument('--headless')  # Run in background
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     driver = webdriver.Chrome(options=options)
#     return driver

# def search_sec_proceedings(driver, keyword):
#     """Search SEC administrative proceedings using Selenium by filling out the form."""
#     # Navigate to the base search page
#     driver.get(SEARCH_URL)
    
#     try:
#         # Find the search input field and enter the keyword
#         keyword_input = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "edit-keywords"))
#         )
#         keyword_input.send_keys(keyword)
        
#         # Find and click the search button
#         search_button = driver.find_element(By.ID, "edit-submit-enforcement-litigation")
#         search_button.click()
        
#     except Exception as e:
#         print(f"Error interacting with the search form: {str(e)}")
#         return []
    
#     # Wait for results table to load
#     try:
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table"))
#         )
#     except:
#         # Check if the page explicitly says no results were found
#         try:
#             no_results_msg = driver.find_element(By.CSS_SELECTOR, ".view-empty")
#             if no_results_msg:
#                 print("No results found for the keyword.")
#                 return []
#         except:
#             print("Timed out waiting for search results to load.")
#             return []
    
#     # Parse the results (your original parsing logic is good)
#     documents = []
#     table = driver.find_element(By.CSS_SELECTOR, "table.views-table")
#     rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    
#     for row in rows:
#         try:
#             cells = row.find_elements(By.TAG_NAME, "td")
#             if len(cells) < 3:
#                 continue
            
#             # Extract date
#             date_str = cells[0].text.strip()
#             try:
#                 release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
#             except ValueError:
#                 try:
#                     release_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
#                 except ValueError:
#                     release_date = date_str
            
#             # Extract company name and PDF URL
#             company_cell = cells[1]
#             company_name = company_cell.text.strip()
            
#             pdf_link = company_cell.find_element(By.TAG_NAME, "a")
#             pdf_url = pdf_link.get_attribute('href')
            
#             # Extract release number
#             release_number = cells[2].text.strip()
            
#             if pdf_url and pdf_url.endswith('.pdf'):
#                 documents.append({
#                     'release_date': release_date,
#                     'company_name': company_name,
#                     'release_number': release_number,
#                     'pdf_url': pdf_url,
#                     'local_path': ''
#                 })
#         except Exception as e:
#             print(f"Error processing a result row: {str(e)}")
            
#     return documents

# def download_pdf(url, filename):
#     """Download a PDF file using requests"""
#     import requests
#     try:
#         headers = {'User-Agent': USER_AGENT}
#         response = requests.get(url, headers=headers, stream=True)
#         response.raise_for_status()
        
#         with open(filename, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         return True
#     except Exception as e:
#         print(f"Error downloading {url}: {str(e)}")
#         return False

# def main():
#     # Create output folder
#     create_output_folder()
    
#     # Setup Selenium
#     driver = setup_selenium()
    
#     try:
#         # Get search keyword from user
#         keyword = input("Enter company name or keyword to search: ").strip()
#         if not keyword:
#             print("No keyword provided. Exiting.")
#             return
        
#         # Search SEC proceedings
#         print(f"Searching SEC proceedings for '{keyword}'...")
#         documents = search_sec_proceedings(driver, keyword)
#         print(f"Found {len(documents)} documents")
        
#         # Download PDFs and update local paths
#         for doc in documents:
#             # Generate filename from company name and date
#             clean_name = ''.join(c if c.isalnum() else '_' for c in doc['company_name'])[:50]
#             filename = f"{clean_name}_{doc['release_date']}.pdf"
#             pdf_path = os.path.join(OUTPUT_FOLDER, filename)
            
#             # Download PDF
#             print(f"Downloading: {doc['company_name']} - {doc['release_date']}")
#             if download_pdf(doc['pdf_url'], pdf_path):
#                 doc['local_path'] = pdf_path
#             time.sleep(1)  # Respectful crawling delay
        
#         # Save results to Excel
#         if documents:
#             df = pd.DataFrame(documents)
#             df.to_excel(EXCEL_FILE, index=False)
#             print(f"Saved {len(documents)} records to {EXCEL_FILE}")
#         else:
#             print("No documents to save")
    
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()



# import os
# import time
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd
# import requests # Make sure requests is imported at the top

# # --- Configuration (remains the same) ---
# USER_AGENT = "Your Name your.name@example.com"
# BASE_URL = "https://www.sec.gov"
# SEARCH_URL = f"{BASE_URL}/enforcement-litigation/administrative-proceedings"
# OUTPUT_FOLDER = "sec_pdfs"
# EXCEL_FILE = "sec_documents.xlsx"


# def create_output_folder():
#     """Create output folder for PDFs if it doesn't exist"""
#     if not os.path.exists(OUTPUT_FOLDER):
#         os.makedirs(OUTPUT_FOLDER)


# def setup_selenium():
#     """Configure Selenium WebDriver"""
#     options = webdriver.ChromeOptions()
#     options.add_argument(f'user-agent={USER_AGENT}')
#     # While debugging, you can comment out the next line to see the browser window
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     driver = webdriver.Chrome(options=options)
#     return driver


# def search_sec_proceedings(driver, keyword):
#     """Search SEC administrative proceedings with a more robust form submission."""
#     driver.get(SEARCH_URL)
    
#     try:
#         # Wait for the keyword input field to be present, then type the keyword
#         keyword_input = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "edit-keywords"))
#         )
#         keyword_input.send_keys(keyword)
        
#         # Explicitly wait for the search button to be clickable
#         search_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "edit-submit-enforcement-litigation"))
#         )
        
#         # Use a JavaScript click for greater reliability
#         driver.execute_script("arguments[0].click();", search_button)
        
#     except Exception as e:
#         print(f"Error interacting with the search form: {str(e)}")
#         # If errors persist, save the page source to see what Selenium is looking at
#         with open("error_page.html", "w", encoding="utf-8") as f:
#             f.write(driver.page_source)
#         return []

#     # Wait for results table to load
#     try:
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table"))
#         )
#     except:
#         try:
#             if driver.find_element(By.CSS_SELECTOR, ".view-empty"):
#                 print("No results found for the keyword.")
#         except:
#             print("Timed out waiting for search results to load.")
#         return []

#     # --- The rest of the parsing logic remains the same ---
#     documents = []
#     table = driver.find_element(By.CSS_SELECTOR, "table.views-table")
#     rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    
#     for row in rows:
#         try:
#             cells = row.find_elements(By.TAG_NAME, "td")
#             if len(cells) < 3:
#                 continue
            
#             date_str = cells[0].text.strip()
#             try:
#                 release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
#             except ValueError:
#                 try:
#                     release_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
#                 except ValueError:
#                     release_date = date_str
            
#             company_cell = cells[1]
#             company_name = company_cell.text.strip()
            
#             pdf_link = company_cell.find_element(By.TAG_NAME, "a")
#             pdf_url = pdf_link.get_attribute('href')
            
#             release_number = cells[2].text.strip()
            
#             if pdf_url and pdf_url.endswith('.pdf'):
#                 documents.append({
#                     'release_date': release_date,
#                     'company_name': company_name,
#                     'release_number': release_number,
#                     'pdf_url': pdf_url,
#                     'local_path': ''
#                 })
#         except Exception as e:
#             print(f"Error processing a result row: {str(e)}")
            
#     return documents


# def download_pdf(url, filename):
#     """Download a PDF file using requests"""
#     try:
#         headers = {'User-Agent': USER_AGENT}
#         response = requests.get(url, headers=headers, stream=True)
#         response.raise_for_status()
        
#         with open(filename, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         return True
#     except Exception as e:
#         print(f"Error downloading {url}: {str(e)}")
#         return False


# def main():
#     """Main execution function"""
#     create_output_folder()
#     driver = setup_selenium()
    
#     try:
#         keyword = input("Enter company name or keyword to search: ").strip()
#         if not keyword:
#             print("No keyword provided. Exiting.")
#             return
            
#         print(f"Searching SEC proceedings for '{keyword}'...")
#         documents = search_sec_proceedings(driver, keyword)
#         print(f"Found {len(documents)} documents")
        
#         if documents:
#             for doc in documents:
#                 clean_name = ''.join(c if c.isalnum() else '_' for c in doc['company_name'])[:50]
#                 filename = f"{clean_name}_{doc['release_date']}.pdf"
#                 pdf_path = os.path.join(OUTPUT_FOLDER, filename)
                
#                 print(f"Downloading: {doc['company_name']} - {doc['release_date']}")
#                 if download_pdf(doc['pdf_url'], pdf_path):
#                     doc['local_path'] = pdf_path
#                 time.sleep(1) 
            
#             df = pd.DataFrame(documents)
#             df.to_excel(EXCEL_FILE, index=False)
#             print(f"Saved {len(documents)} records to {EXCEL_FILE}")
#         else:
#             print("No documents to save")
            
#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     main()



import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Configuration ---
USER_AGENT = "Your Name your.name@example.com"
SEARCH_URL = "https://www.sec.gov/enforcement-litigation/administrative-proceedings"
OUTPUT_FOLDER = "sec_pdfs"
EXCEL_FILE = "sec_documents.xlsx"

def create_output_folder():
    """Create output folder for PDFs if it doesn't exist."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

def search_sec_proceedings(keyword):
    """Search SEC proceedings using requests and parse with BeautifulSoup."""
    print(f"Searching SEC proceedings for '{keyword}'...")
    
    # Form data to be sent with the POST request
    payload = {
        'keywords': keyword,
        'year': 'All',
        'month': 'All',
        'op': 'Search' # This mimics clicking the 'Search' button
    }
    
    # Headers to make the request look like it's from a browser
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': SEARCH_URL
    }
    
    try:
        # Send the POST request
        response = requests.post(SEARCH_URL, data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the results table
        results_table = soup.find("table", class_="views-table")
        if not results_table:
            print("No results found or table structure has changed.")
            return []
            
        documents = []
        # Find all rows in the table body
        for row in results_table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 3:
                continue

            # Extract date from the first cell
            date_str = cells[0].get_text(strip=True)
            try:
                release_date = datetime.strptime(date_str, '%b. %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                try:
                    release_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    release_date = date_str

            # Extract company name and PDF URL from the second cell
            company_cell = cells[1]
            company_name = company_cell.get_text(strip=True)
            pdf_link = company_cell.find('a')
            
            if not pdf_link or not pdf_link.has_attr('href'):
                continue

            pdf_url = pdf_link['href']
            
            # Ensure the link is absolute
            if not pdf_url.startswith('http'):
                pdf_url = f"https://www.sec.gov{pdf_url}"

            # Extract release number from the third cell
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
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
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
    print(f"Found {len(documents)} documents.")
    
    if documents:
        for doc in documents:
            clean_name = ''.join(c for c in doc['company_name'] if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{clean_name.replace(' ', '_')}_{doc['release_date']}.pdf"
            pdf_path = os.path.join(OUTPUT_FOLDER, filename)
            
            print(f"Downloading: {doc['company_name']} ({doc['release_date']})")
            if download_pdf(doc['pdf_url'], pdf_path):
                doc['local_path'] = pdf_path
            time.sleep(1)  # Respectful crawling delay
        
        df = pd.DataFrame(documents)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"\nSaved {len(documents)} records to {EXCEL_FILE}")
    else:
        print("No documents to save.")

if __name__ == "__main__":
    main()