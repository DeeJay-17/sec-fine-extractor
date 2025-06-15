# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import urllib.parse

# def get_press_releases(search_term):
#     # Base URL
#     base_url = "https://www.sec.gov/newsroom/press-releases"
    
#     # Prepare parameters
#     params = {
#         'combine': search_term,
#         'year': 'All',
#         'month': 'All'
#     }
    
#     # Encode the search term for URL
#     encoded_search = urllib.parse.quote_plus(search_term)
    
#     # Construct the full URL
#     full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
#     print(f"Fetching data from: {full_url}")
    
#     try:
#         # Send GET request (POST not needed as this is a simple search form)
#         headers = {
#             'User-Agent': 'your name your.name@email.com'
#         }
#         response = requests.get(full_url, headers=headers)
#         response.raise_for_status()  # Raise an error for bad status codes
        
#         # Parse HTML
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Find all press release links
#         links = []
#         for td in soup.find_all('td', {'headers': 'view-field-display-title-table-column'}):
#             a_tag = td.find('a', href=True)
#             if a_tag:
#                 href = a_tag['href']
#                 if href.startswith('/newsroom/press-releases/'):
#                     full_link = f"https://www.sec.gov{href}"
#                     links.append(full_link)
        
#         # Create DataFrame and save to Excel
#         if links:
#             df = pd.DataFrame({'Press Release Links': links})
#             excel_filename = f"sec_press_releases_{search_term.replace(' ', '_')}.xlsx"
#             df.to_excel(excel_filename, index=False)
#             print(f"Found {len(links)} press releases. Saved to {excel_filename}")
#         else:
#             print("No press releases found for the given search term.")
            
#         return links
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data: {e}")
#         return []

# if __name__ == "__main__":
#     search_term = input("Enter the search term (e.g., 'wells fargo'): ")
#     get_press_releases(search_term)




# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import urllib.parse
# import time

# def get_press_releases(search_term):
#     # Base URL
#     base_url = "https://www.sec.gov/newsroom/press-releases"
    
#     # Prepare parameters
#     params = {
#         'combine': search_term,
#         'year': 'All',
#         'month': 'All'
#     }
    
#     # Encode the search term for URL
#     encoded_search = urllib.parse.quote_plus(search_term)
    
#     # Construct the full URL
#     full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
#     print(f"Fetching data from: {full_url}")
    
#     try:
#         # Send GET request
#         headers = {
#             'User-Agent': 'your name your.name@email.com'
#         }
#         response = requests.get(full_url, headers=headers)
#         response.raise_for_status()
        
#         # Parse HTML
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Find all press release links
#         links = []
#         for td in soup.find_all('td', {'headers': 'view-field-display-title-table-column'}):
#             a_tag = td.find('a', href=True)
#             if a_tag:
#                 href = a_tag['href']
#                 if href.startswith('/newsroom/press-releases/'):
#                     full_link = f"https://www.sec.gov{href}"
#                     links.append(full_link)
        
#         # If no links found, return early
#         if not links:
#             print("No press releases found for the given search term.")
#             return []
        
#         print(f"Found {len(links)} press releases. Now extracting paragraphs...")
        
#         # Prepare data structure for Excel
#         data = []
        
#         for link in links:
#             try:
#                 # Get the press release page
#                 print(f"Processing: {link}")
#                 pr_response = requests.get(link, headers=headers)
#                 pr_response.raise_for_status()
#                 pr_soup = BeautifulSoup(pr_response.text, 'html.parser')
                
#                 # Find the content div
#                 content_div = pr_soup.find('div', {
#                     'class': 'clearfix text-formatted usa-prose field field--name-body field--type-text-with-summary field--label-hidden field__item'
#                 })
                
#                 # Extract all paragraphs
#                 paragraphs = []
#                 if content_div:
#                     for p in content_div.find_all('p'):
#                         paragraph_text = p.get_text(strip=True)
#                         if paragraph_text:  # Skip empty paragraphs
#                             paragraphs.append(paragraph_text)
                
#                 # Combine paragraphs into single text with line breaks
#                 paragraphs_text = '\n\n'.join(paragraphs)
                
#                 # Add to our data
#                 data.append({
#                     'Press Release Link': link,
#                     'Content': paragraphs_text
#                 })
                
#                 # Be polite with a small delay between requests
#                 time.sleep(1)
                
#             except requests.exceptions.RequestException as e:
#                 print(f"Error processing {link}: {e}")
#                 data.append({
#                     'Press Release Link': link,
#                     'Content': f"Error extracting content: {str(e)}"
#                 })
#                 continue
        
#         # Create DataFrame and save to Excel
#         df = pd.DataFrame(data)
#         excel_filename = f"sec_press_releases_{search_term.replace(' ', '_')}.xlsx"
#         df.to_excel(excel_filename, index=False)
#         print(f"Saved {len(data)} press releases with content to {excel_filename}")
        
#         return data
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data: {e}")
#         return []

# if __name__ == "__main__":
#     search_term = input("Enter the search term (e.g., 'wells fargo'): ")
#     get_press_releases(search_term)







import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import time
import os

def get_press_releases(search_term):
    # Base URL
    base_url = "https://www.sec.gov/newsroom/press-releases"
    
    # Encode the search term for URL
    encoded_search = urllib.parse.quote_plus(search_term)
    
    # Construct the full URL
    full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
    print(f"Fetching data from: {full_url}")
    
    try:
        # Send GET request
        headers = {
            'User-Agent': 'your name your.name@email.com'
        }
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all press release links
        links = []
        for td in soup.find_all('td', {'headers': 'view-field-display-title-table-column'}):
            a_tag = td.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith('/newsroom/press-releases/'):
                    full_link = f"https://www.sec.gov{href}"
                    links.append(full_link)
        
        if not links:
            print("No press releases found for the given search term.")
            return []
        
        print(f"Found {len(links)} press releases. Now extracting paragraphs...")
        
        # Prepare data structure
        data = []
        
        for link in links:
            try:
                # Get the press release page
                print(f"Processing: {link}")
                pr_response = requests.get(link, headers=headers)
                pr_response.raise_for_status()
                pr_soup = BeautifulSoup(pr_response.text, 'html.parser')
                
                # Find the content div
                content_div = pr_soup.find('div', {
                    'class': 'clearfix text-formatted usa-prose field field--name-body field--type-text-with-summary field--label-hidden field__item'
                })
                
                # Extract all paragraphs
                paragraphs = []
                if content_div:
                    for p in content_div.find_all('p'):
                        paragraph_text = p.get_text(strip=True)
                        if paragraph_text:
                            paragraphs.append(paragraph_text)
                
                paragraphs_text = '\n\n'.join(paragraphs)
                
                # Add to data with Keyword column
                data.append({
                    'Keyword': search_term,
                    'Press Release Link': link,
                    'Content': paragraphs_text
                })
                
                time.sleep(1)  # Polite delay
                
            except requests.exceptions.RequestException as e:
                print(f"Error processing {link}: {e}")
                data.append({
                    'Keyword': search_term,
                    'Press Release Link': link,
                    'Content': f"Error extracting content: {str(e)}"
                })
                continue
        
        # Excel handling (append if exists)
        excel_filename = "sec_press_releases_combined.xlsx"
        
        if os.path.exists(excel_filename):
            existing_df = pd.read_excel(excel_filename)
            # Filter out links that already exist to avoid duplicates
            existing_links = existing_df['Press Release Link'].tolist()
            new_data = [row for row in data if row['Press Release Link'] not in existing_links]
            
            if new_data:
                new_df = pd.DataFrame(new_data)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                updated_df.to_excel(excel_filename, index=False)
                print(f"Appended {len(new_data)} new results to {excel_filename}")
            else:
                print("No new results to append (all links already exist in the file).")
        else:
            df = pd.DataFrame(data)
            df.to_excel(excel_filename, index=False)
            print(f"Created new file: {excel_filename}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

if __name__ == "__main__":
    search_term = input("Enter the search term (e.g., 'wells fargo'): ")
    get_press_releases(search_term)