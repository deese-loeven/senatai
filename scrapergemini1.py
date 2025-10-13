#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def scrape_bills():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        driver.get("https://www.ola.org/en/legislative-business/bills/current")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )

        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        print(f"Found {len(tables)} tables")

        with open("debug_page.html", "w") as f:
            f.write(driver.page_source)

        if tables:
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")

            bills = []
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    bill_number = cols[0].text.strip()
                    bill_title = cols[1].text.strip()
                    bill_link = cols[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                    bills.append({
                        "number": bill_number,
                        "title": bill_title,
                        "link": bill_link,
                        "source": "main_scraper2" # Added the source tag
                    })

            return bills
        else:
            print("No tables found on the page.")
            return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    bills = scrape_bills()
    if bills:
        with open("billsmainscraper2.json", "w") as f: # Changed the file name
            json.dump(bills, f, indent=4)
        print("Data saved to billsmainscraper2.json")
    else:
        print("No bills scraped.")
