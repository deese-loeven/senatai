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
    # chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        driver.get("https://www.ola.org/en/legislative-business/bills/all")

        # Wait for table to load using the specific selector
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".clearfix.text-formatted.field.field--name-body.field--type-text-with-summary.field--label-hidden.field__item > table"))
        )

        # Extract the specific table
        table = driver.find_element(By.CSS_SELECTOR, ".clearfix.text-formatted.field.field--name-body.field--type-text-with-summary.field--label-hidden.field__item > table")
        print(f"Found table: {table.tag_name}")

        # Extract rows from the table body
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        session_links = []
        # Extract data from the first 10 rows
        for row in rows[:10]:
            link = row.find_element(By.TAG_NAME, "a")
            session_links.append(link.get_attribute("href"))
            print(row.text)

        print("Session links:")
        for link in session_links:
            print(link)

        # Save page for debugging
        with open("debug_page.html", "w") as f:
            f.write(driver.page_source)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_bills()
