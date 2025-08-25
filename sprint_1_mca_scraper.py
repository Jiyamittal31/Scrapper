# sprint_1_mca_scraper.py

import requests
from bs4 import BeautifulSoup
import json
import sys
import time

# --- Configuration ---
# The base URL for the MCA portal's company master data page.
# Note: Government websites can change. This URL is based on the current structure.
BASE_URL = "https://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do"

# Headers to mimic a real web browser, which can help avoid being blocked.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def get_company_details(company_cin: str) -> dict:
    """
    Fetches and parses the master data for a given Company Identification Number (CIN).

    Args:
        company_cin: The 21-character alphanumeric CIN of the company.

    Returns:
        A dictionary containing the scraped company details, or an error message.
    """
    print(f"[*] Attempting to scrape details for CIN: {company_cin}...")

    # The website uses a POST request to submit the search form.
    # We need to simulate this by sending the CIN and a dummy captcha in the payload.
    payload = {
        'companyID': company_cin,
        'displayCaptcha': 'false', # We assume no captcha is needed for this direct access
        'userEnteredCaptcha': 'dummy', # A placeholder value
    }

    try:
        # --- Step 1: Make the HTTP Request ---
        # We use a session object to persist cookies, which can be helpful.
        session = requests.Session()
        response = session.post(BASE_URL, headers=HEADERS, data=payload, timeout=20)

        # Raise an exception if the request was not successful (e.g., 404, 500 errors)
        response.raise_for_status()
        print("[+] Successfully received a response from the server.")

        # --- Step 2: Parse the HTML ---
        # BeautifulSoup will parse the raw HTML text into a navigable object.
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Step 3: Extract the Data ---
        # We find the main table containing the company data.
        # Based on inspection, the data is within a table with id 'resultTab1'.
        result_table = soup.find('table', {'id': 'resultTab1'})

        if not result_table:
            # This can happen if the CIN is invalid or the page structure has changed.
            print("[!] Could not find the result table. The CIN might be invalid or the page layout has changed.")
            return {"error": "Result table not found on the page."}

        company_data = {}
        # Iterate through all rows (<tr>) in the table body (<tbody>).
        for row in result_table.find_all('tr'):
            # Each row contains two cells (<td>): a label and a value.
            cells = row.find_all('td')
            if len(cells) == 2:
                # Clean up the text by removing extra whitespace and newlines.
                key = cells[0].get_text(strip=True).replace(':', '')
                value = cells[1].get_text(strip=True)
                company_data[key] = value

        print(f"[+] Successfully extracted {len(company_data)} data points.")
        return company_data

    except requests.exceptions.RequestException as e:
        print(f"[!] An error occurred during the network request: {e}")
        return {"error": f"Network request failed: {e}"}
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


def save_to_json(data: dict, filename: str):
    """
    Saves the scraped data dictionary to a JSON file.

    Args:
        data: The dictionary to save.
        filename: The name of the output file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # `indent=4` makes the JSON file human-readable.
            # `ensure_ascii=False` is important for handling non-English characters.
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[+] Data successfully saved to {filename}")
    except IOError as e:
        print(f"[!] Failed to save data to file: {e}")


# --- Main Execution Block ---
if __name__ == "__main__":
    # This block runs when the script is executed directly from the command line.
    print("--- MCA Company Data Scraper ---")

    # Example CIN for a well-known company (Infosys Limited).
    # You can replace this with any valid CIN.
    # We check if a CIN was passed as a command-line argument.
    if len(sys.argv) > 1:
        target_cin = sys.argv[1]
    else:
        # Use a default CIN if none is provided.
        target_cin = "L85110KA1981PLC013115"
        print(f"[*] No CIN provided. Using default example CIN for Infosys: {target_cin}")

    # Fetch the company details.
    scraped_data = get_company_details(target_cin)

    # If data was successfully scraped (no error key), save it.
    if scraped_data and "error" not in scraped_data:
        output_filename = f"{target_cin}_details.json"
        save_to_json(scraped_data, output_filename)
    else:
        print("[!] Scraping failed. No data was saved.")

    print("--- Scraper finished ---")
