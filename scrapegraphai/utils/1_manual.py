import requests
import logging
import time
from urllib.parse import quote, urljoin
from typing import Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
import markdownify

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_content(token: str, target_url: str, max_retries: int = 5, retry_delay: int = 3) -> Optional[str]:
    encoded_url = quote(target_url)
    url = f"http://api.scrape.do?url={encoded_url}&token={token}&render=true&waitUntil=networkidle0"

    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f"Successfully fetched content from {target_url}")
                return response.text
            logging.warning(f"Failed with status {response.status_code}. Retrying in {retry_delay}s...")
        except requests.RequestException as e:
            logging.error(f"Error fetching {target_url}: {e}. Retrying in {retry_delay}s...")
        time.sleep(retry_delay)

    logging.error(f"Failed to fetch {target_url} after {max_retries} attempts.")
    return None

def extract_links(html_content: str) -> list:
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [link['href'] for link in soup.find_all('a', href=True)]
    logging.info(f"Extracted {len(links)} links.")
    return links

def process_links(token: str, base_url: str, links: list, depth: int, current_depth: int = 1) -> dict:
    content_dict = {}
    for idx, link in enumerate(links, start=1):
        full_link = link if link.startswith("http") else urljoin(base_url, link)
        logging.info(f"Processing link {idx}: {full_link}")
        link_content = fetch_content(token, full_link)
        if link_content:
            markdown_content = markdownify.markdownify(link_content, heading_style="ATX")
            content_dict[full_link] = markdown_content
            save_content_to_json(content_dict, idx)

            if current_depth < depth:
                new_links = extract_links(link_content)
                content_dict.update(process_links(token, full_link, new_links, depth, current_depth + 1))
        else:
            logging.warning(f"Failed to fetch content for {full_link}")
    return content_dict

def save_content_to_json(content_dict: dict, idx: int):
    if not os.path.exists("downloaded_pages"):
        os.makedirs("downloaded_pages")

    file_name = f"scraped_content_{idx}.json"
    file_path = os.path.join("downloaded_pages", file_name)

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(content_dict, json_file, ensure_ascii=False, indent=4)

    logging.info(f"Content saved to {file_path}")

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    target_url = "https://www.wired.com"
    depth = 2 

    if not token or not target_url:
        logging.error("Please set the TOKEN and TARGET_URL environment variables.")
        exit(1)

    html_content = fetch_content(token, target_url)

    if html_content:
        links = extract_links(html_content)
        logging.info("Links found:")
        for link in links:
            logging.info(link)

        content_dict = process_links(token, target_url, links, depth)
        for link, content in content_dict.items():
            logging.info(f"Link: {link}")
            logging.info(f"Content: {content[:500]}...") 
    else:
        logging.error("Failed to fetch the content.")
