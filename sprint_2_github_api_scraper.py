# sprint_2_github_api_scraper.py

import requests
import json
import sys
import os
import time
from datetime import datetime

# --- Configuration ---
# Base URL for the GitHub REST API.
API_BASE_URL = "https://api.github.com"

def check_rate_limit(headers: dict):
    """
    Checks the rate limit status from the API response headers and prints it.

    Args:
        headers: The dictionary of response headers from the requests library.
    """
    # GitHub provides rate limit information in the response headers.
    remaining = int(headers.get('X-RateLimit-Remaining', 0))
    limit = int(headers.get('X-RateLimit-Limit', 0))
    reset_timestamp = int(headers.get('X-RateLimit-Reset', 0))

    # Convert the reset timestamp to a human-readable format.
    reset_time = datetime.fromtimestamp(reset_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    print(f"[i] Rate Limit Info: {remaining}/{limit} requests remaining. Resets at {reset_time}.")
    if remaining == 0:
        print("[!] Warning: Rate limit exhausted. Waiting until reset time.")
        # In a real application, you would implement a waiting mechanism here.
        # time.sleep(reset_timestamp - time.time() + 1)


def get_github_user_data(username: str, token: str = None) -> dict:
    """
    Fetches public profile and repository data for a given GitHub username using the API.

    Args:
        username: The GitHub username to look up.
        token: A GitHub Personal Access Token for authenticated requests (optional but recommended).

    Returns:
        A dictionary containing the combined user and repository data, or an error message.
    """
    print(f"\n[*] Attempting to fetch data for user: {username}...")
    user_url = f"{API_BASE_URL}/users/{username}"

    # --- Step 1: Set up Authentication ---
    # Authenticated requests have a much higher rate limit (5000/hr vs 60/hr).
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Verified-Job-Marketplace-Scraper'
    }
    if token:
        print("[i] Using Personal Access Token for authentication.")
        headers['Authorization'] = f"token {token}"
    else:
        print("[!] Warning: Making unauthenticated request. Rate limit is very low (60/hr).")

    try:
        # --- Step 2: Fetch User Profile Data ---
        response = requests.get(user_url, headers=headers, timeout=20)
        check_rate_limit(response.headers)
        response.raise_for_status() # Raises an exception for 4xx or 5xx status codes

        user_data = response.json()
        print(f"[+] Successfully fetched profile for '{user_data.get('name')}' (@{user_data.get('login')}).")

        # --- Step 3: Fetch Repository Data ---
        repos_url = user_data.get('repos_url')
        if not repos_url:
            return {"error": "Could not find repository URL for the user."}

        repo_response = requests.get(repos_url, headers=headers, timeout=20)
        check_rate_limit(repo_response.headers)
        repo_response.raise_for_status()

        repos_data = repo_response.json()
        print(f"[+] Found {len(repos_data)} public repositories.")

        # --- Step 4: Extract Key Repository Information ---
        # We don't need all the repo data, just the "signals" we defined.
        repo_signals = []
        for repo in repos_data:
            signal = {
                "name": repo.get("name"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
            }
            repo_signals.append(signal)

        # --- Step 5: Combine and Return Data ---
        combined_data = {
            "profile": user_data,
            "repositories": repo_signals
        }
        return combined_data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"[!] Error: User '{username}' not found.")
            return {"error": f"User '{username}' not found."}
        else:
            print(f"[!] HTTP Error: {e}")
            return {"error": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        print(f"[!] Network request failed: {e}")
        return {"error": f"Network request failed: {e}"}

def save_to_json(data: dict, filename: str):
    """Saves the scraped data dictionary to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[+] Data successfully saved to {filename}")
    except IOError as e:
        print(f"[!] Failed to save data to file: {e}")

# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- GitHub User Data Scraper (API-First) ---")

    # We expect the username as the first argument, and the token as the second (optional).
    if len(sys.argv) < 2:
        print("Usage: python sprint_2_github_api_scraper.py <username> [github_token]")
        print("Example: python sprint_2_github_api_scraper.py torvalds")
        print("You can also set the GITHUB_TOKEN environment variable.")
        sys.exit(1)

    target_username = sys.argv[1]
    # Get token from command line argument or environment variable
    github_token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('GITHUB_TOKEN')

    scraped_data = get_github_user_data(target_username, github_token)

    if scraped_data and "error" not in scraped_data:
        output_filename = f"{target_username}_github_data.json"
        save_to_json(scraped_data, output_filename)
    else:
        print("[!] Scraping failed. No data was saved.")

    print("\n--- Scraper finished ---")
