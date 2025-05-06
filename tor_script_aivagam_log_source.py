import time
import requests
import random
import urllib.parse
from stem import Signal
from stem.control import Controller
from datetime import datetime

# === Tor Proxy Settings ===
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050

# === Base Google Search URL ===
base_google_search_url = "https://www.google.co.in/search?client={client}&q={search_query}"

# === User-Agent, Language, Referer, Encoding Lists ===
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0)...',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4)...'
]

accept_languages = [
    'en-US,en;q=0.9',
    'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'es-ES,es;q=0.9,en;q=0.8',
    'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
]

referers = [
    'https://www.google.com/',
    'https://www.reddit.com/r/Python/',
    'https://www.stackoverflow.com/',
    'https://www.github.com/'
]

accept_encodings = [
    'gzip, deflate, br',
    'gzip, deflate',
    'identity',
    'gzip, deflate, *;q=0.8'
]

# === Functions ===

def read_search_queries(file_path):
    """Read search queries from a text file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            queries = [line.strip() for line in file.readlines() if line.strip()]
        return queries
    except FileNotFoundError:
        print(f"[!] The file {file_path} was not found.")
        return []

def generate_client():
    return random.choice(['ubuntu-sn', 'chrome', 'firefox', 'android', 'iphone', 'ipad'])

def generate_search_query(search_queries):
    """Select a random search query from the list."""
    query = random.choice(search_queries)
    encoded_query = urllib.parse.quote(query)
    return encoded_query.replace('%20', '+')

def build_headers():
    return {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': random.choice(accept_languages),
        'Accept-Encoding': random.choice(accept_encodings),
        'Referer': random.choice(referers)
    }

def send_request(url):
    session = requests.Session()
    session.proxies = {
        'http': f'socks5://{TOR_HOST}:{TOR_PORT}',
        'https': f'socks5://{TOR_HOST}:{TOR_PORT}'
    }
    session.headers.update(build_headers())

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "Unknown"
    ip = "unknown"
    status_code = "?"

    try:
        print(f"[i] Sending request to {url}...")  # Display the URL being requested
        response = session.get(url, timeout=20)
        status_code = response.status_code
        status = "Success"

        if "Our systems have detected unusual traffic" in response.text or "To continue, please verify" in response.text:
            status = "CAPTCHA"

        # Get outbound IP
        ip_response = session.get("http://httpbin.org/ip")
        ip = ip_response.json().get("origin", "unknown")

        print(f"[✓] Request successful. Status Code: {status_code} | IP: {ip}")  # Show status and IP

    except requests.RequestException as e:
        status = f"Request Error: {e}"
        print(f"[!] Request failed: {e}")  # Show error details

    log_entry = f"{timestamp} | URL: {url} | Status Code: {status_code} | IP: {ip} | Status: {status}"

    # Write to log file
    with open("tor_script_log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

def change_tor_ip():
    try:
        print("[i] Requesting a new IP address from Tor...")
        with Controller.from_port(port=9051) as controller:
            controller.authenticate("welcome12345")
            controller.signal(Signal.NEWNYM)
            time.sleep(5)
        print("[✓] New IP successfully assigned.")
    except Exception as e:
        print(f"[!] Failed to change IP: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("tor_script_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} | ERROR: Failed to change Tor IP: {e}\n")

# === Main Execution ===

def main():
    search_queries = read_search_queries("tor_aivagam_source.txt")  # Read queries from the text file
    if not search_queries:
        print("[!] No search queries found. Exiting script.")
        return

    try:
        while True:
            search_query = generate_search_query(search_queries)  # Get a random search query from the file
            client = generate_client()
            search_url = base_google_search_url.format(client=client, search_query=search_query)

            send_request(search_url)
            change_tor_ip()

            wait_time = random.randint(60, 120)
            print(f"[i] Waiting {wait_time} seconds before sending next request...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n[!] Script interrupted by user.")

if __name__ == "__main__":
    main()

