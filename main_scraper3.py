#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

def scrape_ontario_bills(output_dir="data"):
    """
    Scrapes current Ontario bills from the legislative website.

    Args:
        output_dir (str): Directory to save scraped data.
    """
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")  # Comment out for visible browser
    chrome_options.add_argument("--disable-gpu") # Recommended for headless, and sometimes needed for visible
    chrome_options.add_argument("--no-sandbox") # Potentially needed for docker, or some linux systems.

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

        driver.get("https://www.ola.org/en/legislative-business/bills/current")

        # Wait for table to load with explicit waits.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )

        # Wait for table rows and columns to load.
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "td"))
        )

        tables = driver.find_elements(By.CSS_SELECTOR, "table")

        if tables:
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")

            bills = []
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    bill_number = cols[0].text.strip()
                    bill_title_element = cols[1].find_element(By.TAG_NAME, "a")
                    bill_title = bill_title_element.text.strip()
                    bill_link = bill_title_element.get_attribute("href")

                    #Navigate to bill link and get more information.
                    driver.get(bill_link)

                    #Wait for page to load.
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.field--name-field-bill-status"))
                    )

                    status_element = driver.find_element(By.CSS_SELECTOR, "div.field--name-field-bill-status .field__item")
                    status = status_element.text.strip()

                    bills.append({
                        "number": bill_number,
                        "title": bill_title,
                        "link": bill_link,
                        "status": status,
                    })
                    driver.back() #navigate back to bill list.

            # Save the scraped data to a JSON file.
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "ontario_bills.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(bills, f, ensure_ascii=False, indent=4)

            print(f"Scraped {len(bills)} bills and saved to {output_file}")

        else:
            print("No tables found on the page.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if "driver" in locals():
            driver.quit()

if __name__ == "__main__":
    scrape_ontario_bills()
