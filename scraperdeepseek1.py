#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class BillScraper:
    def __init__(self):
        self.db_conn = sqlite3.connect('ontario_bills.db')
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT,
                last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_data TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bills_scraped INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        self.db_conn.commit()

    def _store_bill(self, bill_data):
        """Store bill data in database"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO bills 
                (bill_number, title, url, source, raw_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                bill_data['number'],
                bill_data['title'],
                bill_data['link'],
                bill_data.get('source', 'main_scraper2'),
                json.dumps(bill_data) if 'raw_data' not in bill_data else bill_data['raw_data']
            ))
            self.db_conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Database error storing bill {bill_data['number']}: {e}")
            return False

    def scrape_bills(self):
        """Main scraping function"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Re-enable headless when working
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = None
        scraped_count = 0
        start_time = time.time()
        
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )

            driver.get("https://www.ola.org/en/legislative-business/bills/current")
            logging.info("Loaded bills page")

            # Wait for the main content to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-bills"))
            )

            # Save debug page source
            with open("debug_page.html", "w", encoding='utf-8') as f:
                f.write(driver.page_source)

            # Find all tables (using more specific selector)
            tables = driver.find_elements(By.CSS_SELECTOR, "table.table-bills")
            logging.info(f"Found {len(tables)} bill tables")

            if not tables:
                logging.warning("No bill tables found")
                return 0

            bills = []
            table = tables[0]
            rows = WebDriverWait(table, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )

            for row in rows[1:]:  # Skip header row
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        bill_number = cols[0].text.strip()
                        bill_title = cols[1].text.strip()
                        bill_link = cols[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                        
                        bill_data = {
                            "number": bill_number,
                            "title": bill_title,
                            "link": bill_link,
                            "source": "main_scraper2"
                        }
                        
                        if self._store_bill(bill_data):
                            bills.append(bill_data)
                            scraped_count += 1
                except Exception as e:
                    logging.warning(f"Error processing row: {e}")
                    continue

            # Save to JSON as backup
            with open(f"bills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                json.dump(bills, f, indent=4)

            return scraped_count

        except Exception as e:
            logging.error(f"Scraping failed: {str(e)}", exc_info=True)
            return 0
            
        finally:
            # Log scraping session
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO scraping_log 
                (bills_scraped, status, error_message)
                VALUES (?, ?, ?)
            ''', (
                scraped_count,
                'success' if scraped_count > 0 else 'failed',
                '' if scraped_count > 0 else 'No bills scraped'
            ))
            self.db_conn.commit()
            
            if driver:
                driver.quit()
            logging.info(f"Scraping completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    scraper = BillScraper()
    count = scraper.scrape_bills()
    scraper.db_conn.close()
    
    if count > 0:
        print(f"Successfully scraped {count} bills")
    else:
        print("No bills were scraped")
