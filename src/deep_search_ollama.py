import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(prompt):
    words = word_tokenize(prompt.lower())
    stop_words = set(stopwords.words('english'))
    return [w for w in words if w.isalnum() and w not in stop_words]

def fetch_and_parse(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def extract_text_from_tags(soup, tags):
    content = []
    for tag in tags:
        elements = soup.find_all(tag)
        for el in elements:
            text = el.get_text(strip=True)
            if text:
                content.append(text)
    return content

def crawl_links(base_url, keywords, tags, max_pages=5):
    visited = set()
    to_visit = set([base_url])
    scraped_pages = 0
    parsed_base = urlparse(base_url).netloc
    results = []

    while to_visit and scraped_pages < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue

        soup = fetch_and_parse(url)
        if soup is None:
            continue

        print(f"Scraping: {url}")
        visited.add(url)
        scraped_pages += 1

        content = extract_text_from_tags(soup, tags)
        if content:
            results.append((url, content))

        # Look for internal links with keyword matches
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            full_url = urljoin(url, href)
            parsed_link = urlparse(full_url)

            if parsed_link.netloc != parsed_base:
                continue  # Only crawl internal links

            text = link_tag.get_text(strip=True).lower()
            if any(keyword in text or keyword in href.lower() for keyword in keywords):
                if full_url not in visited:
                    to_visit.add(full_url)

    return results

def main():
    base_url = input("Enter the base URL to scrape: ").strip()
    if not base_url:
        print("Base URL required.")
        return

    prompt = input("Enter your query: ").strip()
    if not prompt:
        print("Prompt required.")
        return

    keywords = extract_keywords(prompt)
    tags_to_extract = ['title', 'h1', 'h2', 'h3', 'p']

    results = crawl_links(base_url, keywords, tags_to_extract)

    with open('output.md', 'w', encoding='utf-8') as f:
        f.write(f"# Scraped results for: {prompt}\n\n")
        for url, texts in results:
            f.write(f"\n--- {url} ---\n")
            for line in texts:
                f.write(f"- {line}\n")

    print("✅ Done! Scraped content saved to output.txt.")

if __name__ == "__main__":
    main()
