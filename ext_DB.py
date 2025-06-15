import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time
import urllib.parse

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('sec_press_releases.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS press_releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        link TEXT UNIQUE,
        penalty_amount TEXT,
        content TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Extract penalty amount from text
def extract_penalty_amount(text):
    # Patterns to match: $900,000 / $60 million / $1.2 billion etc.
    patterns = [
        r'\$\d{1,3}(?:,\d{3})+(?:\.\d+)?',  # $900,000 / $1,000,000.00
        r'\$\d+\.?\d*\s?million',            # $60 million / $1.5 million
        r'\$\d+\.?\d*\s?billion',             # $1 billion / $2.5 billion
        r'\$\d+\.?\d*\s?[Mm]',                # $60M / $1.5M
        r'\$\d+\.?\d*\s?[Bb]'                 # $1B / $2.5B
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first match (most likely the penalty amount)
            return matches[0]
    return None

# Main scraping function
def get_press_releases(search_term):
    base_url = "https://www.sec.gov/newsroom/press-releases"
    encoded_search = urllib.parse.quote_plus(search_term)
    full_url = f"{base_url}?combine={encoded_search}&year=All&month=All"
    
    print(f"Fetching data from: {full_url}")
    
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
        
        print(f"Found {len(links)} press releases. Processing...")
        
        conn = sqlite3.connect('sec_press_releases.db')
        cursor = conn.cursor()
        
        for link in links:
            try:
                # Check if link already exists in DB
                cursor.execute("SELECT 1 FROM press_releases WHERE link = ?", (link,))
                if cursor.fetchone():
                    print(f"Skipping duplicate: {link}")
                    continue
                
                # Fetch press release content
                print(f"Processing: {link}")
                pr_response = requests.get(link, headers=headers)
                pr_response.raise_for_status()
                pr_soup = BeautifulSoup(pr_response.text, 'html.parser')
                
                # Extract content
                content_div = pr_soup.find('div', {
                    'class': 'clearfix text-formatted usa-prose field field--name-body field--type-text-with-summary field--label-hidden field__item'
                })
                
                content = '\n\n'.join(p.get_text(strip=True) for p in content_div.find_all('p') if p.get_text(strip=True)) if content_div else ""
                
                # Extract penalty amount
                penalty_amount = extract_penalty_amount(content) if content else None
                
                # Insert into database
                cursor.execute('''
                INSERT INTO press_releases (keyword, link, penalty_amount, content)
                VALUES (?, ?, ?, ?)
                ''', (search_term, link, penalty_amount, content))
                
                conn.commit()
                time.sleep(1)  # Polite delay
                
            except Exception as e:
                print(f"Error processing {link}: {str(e)}")
                continue
        
        conn.close()
        print("Data saved to database successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Main execution
if __name__ == "__main__":
    init_db()
    search_term = input("Enter search term (e.g., 'wells fargo'): ")
    get_press_releases(search_term)
    
    # Show sample data
    conn = sqlite3.connect('sec_press_releases.db')
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, penalty_amount FROM press_releases ORDER BY id DESC LIMIT 5")
    print("\nRecent entries:")
    for row in cursor.fetchall():
        print(f"Keyword: {row[0]}, Penalty: {row[1] or 'Not found'}")
    conn.close()