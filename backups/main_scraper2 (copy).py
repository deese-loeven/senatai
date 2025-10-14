#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_bills():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get("https://www.ola.org/en/legislative-business/bills/current")
        
        # Wait for table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        
        # Extract all tables
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        print(f"Found {len(tables)} tables")
        
        # Save page for debugging
        with open("debug_page.html", "w") as f:
            f.write(driver.page_source)
            
        # Extract data from the first table (assuming it's the relevant one)
        if tables:
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            bills = []
            for row in rows[1:]:  # Skip the header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    bill_number = cols[0].text.strip()
                    bill_title = cols[1].text.strip()
                    bill_link = cols[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                    bills.append({"number": bill_number, "title": bill_title, "link": bill_link})
                    
            return bills
        else:
            print("No tables found on the page.")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
        
    finally:
        if 'driver' in locals(): #check if the driver was initialized before trying to quit.
            driver.quit()

if __name__ == "__main__":
    bills = scrape_bills()
    if bills:
        for bill in bills:
            print(f"Bill Number: {bill['number']}")
            print(f"Bill Title: {bill['title']}")
            print(f"Bill Link: {bill['link']}")
            print("-" * 20)
