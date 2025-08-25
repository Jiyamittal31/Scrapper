# sprint_3_dynamic_scraper.py

import json
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
# Target URL: A public career page known for loading jobs dynamically.
# We'll use a public-facing example that is suitable for this demonstration.
# This example targets the careers page for NVIDIA.
TARGET_URL = "https://www.nvidia.com/en-us/about-nvidia/careers/search-jobs/"

def scrape_dynamic_jobs() -> list:
    """
    Scrapes job listings from a dynamic, JavaScript-driven career page using Selenium.

    Returns:
        A list of dictionaries, where each dictionary represents a job listing.
    """
    print("[*] Initializing Selenium WebDriver...")

    # --- Step 1: Set up the Selenium WebDriver ---
    # This uses webdriver_manager to automatically download and manage the correct
    # driver for your installed Chrome version. This is much easier than manual setup.
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no browser window opens)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None # Initialize driver to None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("[+] WebDriver initialized successfully.")

        # --- Step 2: Navigate to the Page ---
        print(f"[*] Navigating to {TARGET_URL}...")
        driver.get(TARGET_URL)

        # --- Step 3: Wait for Dynamic Content to Load ---
        # This is the most critical step. We wait up to 30 seconds for the container
        # holding the job listings to become visible. The selector is found by
        # inspecting the page in a browser's DevTools.
        print("[*] Waiting for job listings to load dynamically...")
        wait = WebDriverWait(driver, 30)
        job_list_container_selector = "ul.job-list" # CSS selector for the job list
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, job_list_container_selector)))
        print("[+] Job listings container is now visible.")

        # Optional: You might need to simulate scrolling to load all jobs
        # for pages with "infinite scroll".
        # for _ in range(3): # Scroll down 3 times
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     time.sleep(3) # Wait for new content to load

        # --- Step 4: Extract the Data ---
        # Now that the content is loaded, we can find the job elements.
        job_elements = driver.find_elements(By.CSS_SELECTOR, "li.job-list-item")
        print(f"[+] Found {len(job_elements)} job listings on the page.")

        if not job_elements:
            print("[!] No job listings were found. The page structure may have changed.")
            return []

        scraped_jobs = []
        for job_element in job_elements:
            try:
                # Extract title, location, and the link (href) from the child elements.
                # These selectors are specific to the target site and can break if it changes.
                title_element = job_element.find_element(By.CSS_SELECTOR, "h3 a")
                title = title_element.text
                link = title_element.get_attribute('href')
                
                location_element = job_element.find_element(By.CSS_SELECTOR, "span.job-location")
                location = location_element.text

                job_data = {
                    "title": title,
                    "location": location,
                    "url": link,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                scraped_jobs.append(job_data)
            except Exception as e:
                # This catches errors if a single job listing has a different structure.
                print(f"[!] Warning: Could not parse a job listing. Error: {e}")
        
        return scraped_jobs

    except TimeoutException:
        print("[!] Error: Timed out waiting for the job listings to load.")
        print("[!] This could be due to a slow network, a change in the website's structure, or anti-scraping measures.")
        return []
    except WebDriverException as e:
        print(f"[!] WebDriver Error: {e}")
        print("[!] Ensure you have Google Chrome installed.")
        return []
    finally:
        # --- Step 5: Clean Up ---
        # It's crucial to close the browser session to free up resources.
        if driver:
            driver.quit()
            print("[*] WebDriver session closed.")

def save_to_json(data: list, filename: str):
    """Saves the scraped data list to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[+] Data successfully saved to {filename}")
    except IOError as e:
        print(f"[!] Failed to save data to file: {e}")

# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- Dynamic Web Page Scraper (Selenium) ---")
    
    scraped_data = scrape_dynamic_jobs()

    if scraped_data:
        output_filename = "dynamic_job_listings.json"
        save_to_json(scraped_data, output_filename)
    else:
        print("[!] Scraping failed or no data was found. No file was saved.")

    print("\n--- Scraper finished ---")
