# import requests
# from bs4 import BeautifulSoup
# import sqlite3
# import re
# import time
# import urllib.parse

# def init_db():
#     conn = sqlite3.connect('sec_press_releases.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS press_releases (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         keyword TEXT,
#         link TEXT UNIQUE,
#         penalty_amount TEXT,
#         content TEXT
#     )
#     ''')
#     conn.commit()
#     conn.close()

# def standardize_penalty(penalty_text):
#     if not penalty_text:
#         return None
    
#     clean_text = penalty_text.strip().replace('$', '').replace(',', '').lower()
    
#     try:
#         if 'million' in clean_text or 'm' in clean_text:
#             number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
#             return f"{int(float(number) * 1000000):,}"
#         elif 'billion' in clean_text or 'b' in clean_text:
#             number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
#             return f"{int(float(number) * 1000000000):,}"
#         else:
#             number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
#             return f"{int(float(number)):,}"
#     except (AttributeError, ValueError):
#         return None

# def get_press_releases(search_term):
#     base_url = "https://www.sec.gov/newsroom/press-releases"
#     encoded_search = urllib.parse.quote_plus(search_term)
#     full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
    
#     try:
#         headers = {'User-Agent': 'your name your.name@email.com'}
#         response = requests.get(full_url, headers=headers)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         links = []
        
#         for td in soup.find_all('td', {'headers': 'view-field-display-title-table-column'}):
#             if a_tag := td.find('a', href=True):
#                 if href := a_tag['href']:
#                     if href.startswith('/newsroom/press-releases/'):
#                         links.append(f"https://www.sec.gov{href}")
        
#         if not links:
#             print("No press releases found.")
#             return
        
#         conn = sqlite3.connect('sec_press_releases.db')
#         cursor = conn.cursor()
        
#         for link in links:
#             try:
#                 cursor.execute("SELECT 1 FROM press_releases WHERE link = ?", (link,))
#                 if cursor.fetchone():
#                     print(f"Skipping duplicate: {link}")
#                     continue
                
#                 pr_response = requests.get(link, headers=headers)
#                 pr_response.raise_for_status()
#                 pr_soup = BeautifulSoup(pr_response.text, 'html.parser')
                
#                 content_div = pr_soup.find('div', {
#                     'class': 'clearfix text-formatted usa-prose field field--name-body field--type-text-with-summary field--label-hidden field__item'
#                 })
#                 content = '\n\n'.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else ""
                
#                 penalty_match = re.search(r'\$\d+\.?\d*\s?(?:million|billion|m|b)|\$\d{1,3}(?:,\d{3})+(?:\.\d+)?', content, re.IGNORECASE)
#                 penalty_amount = standardize_penalty(penalty_match.group(0)) if penalty_match else None
                
#                 cursor.execute('''
#                 INSERT INTO press_releases (keyword, link, penalty_amount, content)
#                 VALUES (?, ?, ?, ?)
#                 ''', (search_term, link, penalty_amount, content))
                
#                 conn.commit()
#                 time.sleep(1)
                
#             except Exception as e:
#                 print(f"Error processing {link}: {str(e)}")
#                 continue
        
#         conn.close()
#         print("Data saved to database successfully!")
        
#     except Exception as e:
#         print(f"Error: {str(e)}")

# if __name__ == "__main__":
#     init_db()
#     search_term = input("Enter search term (e.g., 'wells fargo'): ")
#     get_press_releases(search_term)
    
#     conn = sqlite3.connect('sec_press_releases.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT keyword, penalty_amount FROM press_releases ORDER BY id DESC LIMIT 5')
    
#     print("\nRecent entries:")
#     for row in cursor.fetchall():
#         print(f"{row[0]}: {row[1] or 'No penalty found'}")
#     conn.close()







import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time
import urllib.parse

def init_db():
    conn = sqlite3.connect('sec_press_releases.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS press_releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        link TEXT UNIQUE,
        date TEXT,            -- Raw date as it appears (e.g., "Jan. 17, 2025")
        penalty_amount TEXT,  -- Standardized format (e.g., "7,000,000")
        content TEXT
    )
    ''')
    conn.commit()
    conn.close()

def extract_date(soup):
    date_div = soup.find('div', {
        'class': 'field field--name-dynamic-twig-fieldnode-press-release-lead-in field--type-ds field--label-hidden field__item'
    })
    if date_div:
        date_text = date_div.get_text(strip=True)
        # Extract just the date portion (e.g., "Jan. 17, 2025")
        date_match = re.search(r'([A-Za-z]+\.? \d{1,2}, \d{4})', date_text)
        if date_match:
            return date_match.group(1).strip()
    return None

def standardize_penalty(penalty_text):
    if not penalty_text:
        return None
    
    clean_text = penalty_text.strip().replace('$', '').replace(',', '').lower()
    
    try:
        if 'million' in clean_text or 'm' in clean_text:
            number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
            return f"{int(float(number) * 1000000):,}"
        elif 'billion' in clean_text or 'b' in clean_text:
            number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
            return f"{int(float(number) * 1000000000):,}"
        else:
            number = re.search(r'(\d+\.?\d*)', clean_text).group(1)
            return f"{int(float(number)):,}"
    except (AttributeError, ValueError):
        return None

def get_press_releases(search_term):
    base_url = "https://www.sec.gov/newsroom/press-releases"
    encoded_search = urllib.parse.quote_plus(search_term)
    full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
    
    try:
        headers = {'User-Agent': 'your name your.name@email.com'}
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for td in soup.find_all('td', {'headers': 'view-field-display-title-table-column'}):
            if a_tag := td.find('a', href=True):
                if href := a_tag['href']:
                    if href.startswith('/newsroom/press-releases/'):
                        links.append(f"https://www.sec.gov{href}")
        
        if not links:
            print("No press releases found.")
            return
        
        conn = sqlite3.connect('sec_press_releases.db')
        cursor = conn.cursor()
        
        for link in links:
            try:
                cursor.execute("SELECT 1 FROM press_releases WHERE link = ?", (link,))
                if cursor.fetchone():
                    print(f"Skipping duplicate: {link}")
                    continue
                
                pr_response = requests.get(link, headers=headers)
                pr_response.raise_for_status()
                pr_soup = BeautifulSoup(pr_response.text, 'html.parser')
                
                # Extract raw date text
                release_date = extract_date(pr_soup)
                
                # Extract content
                content_div = pr_soup.find('div', {
                    'class': 'clearfix text-formatted usa-prose field field--name-body field--type-text-with-summary field--label-hidden field__item'
                })
                content = '\n\n'.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else ""
                
                # Extract and standardize penalty
                penalty_match = re.search(r'\$\d+\.?\d*\s?(?:million|billion|m|b)|\$\d{1,3}(?:,\d{3})+(?:\.\d+)?', content, re.IGNORECASE)
                penalty_amount = standardize_penalty(penalty_match.group(0)) if penalty_match else None
                
                # Insert into database
                cursor.execute('''
                INSERT INTO press_releases (keyword, link, date, penalty_amount, content)
                VALUES (?, ?, ?, ?, ?)
                ''', (search_term, link, release_date, penalty_amount, content))
                
                conn.commit()
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {link}: {str(e)}")
                continue
        
        conn.close()
        print("Data saved to database successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    init_db()
    search_term = input("Enter search term (e.g., 'wells fargo'): ")
    get_press_releases(search_term)
    
    conn = sqlite3.connect('sec_press_releases.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT keyword, date, penalty_amount 
    FROM press_releases 
    ORDER BY id DESC 
    LIMIT 5
    ''')
    
    print("\nRecent entries:")
    for row in cursor.fetchall():
        print(f"{row[0]} | {row[1] or 'No date'} | {row[2] or 'No penalty'}")
    conn.close()