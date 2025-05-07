import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(prompt, language='english'):
    words = word_tokenize(prompt.lower())
    stop_words = set(stopwords.words(language))
    keywords = [w for w in words if w.isalnum() and w not in stop_words]
    # Ajouter des synonymes pour "dark"
    if 'dark' in keywords:
        if language == 'french':
            keywords.extend(['sombre', 'noir', 'obscur'])
        else:
            keywords.extend(['shadow', 'dim', 'gloomy'])
    return keywords

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

        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            full_url = urljoin(url, href)
            parsed_link = urlparse(full_url)

            if parsed_link.netloc != parsed_base:
                continue

            text = link_tag.get_text(strip=True).lower()
            if any(keyword in text or keyword in href.lower() for keyword in keywords):
                if full_url not in visited:
                    to_visit.add(full_url)

    return results

def filter_relevant_content(md_file, keywords, prompt, max_chars=4000, min_length=10):
    irrelevant_terms = [
        'sommaire', 'références', 'voir aussi', 'liens externes', 'modifier', 'wikidata',
        'articles connexes', 'bibliographie', 'identification', 'suivi', 'historique'
    ]
    relevant_content = []
    current_url = None
    char_count = 0

    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('---'):
            current_url = line.replace('---', '').strip()
            continue
        if line.startswith('-') and current_url:
            text = line[2:].strip()
            if len(text) < min_length or any(term.lower() in text.lower() for term in irrelevant_terms):
                continue
            if any(keyword in text.lower() for keyword in keywords):
                # Vérifier si l'ajout dépasse la limite de caractères
                line_chars = len(f"From {current_url}:\n- {text}\n")
                if char_count + line_chars > max_chars:
                    break
                relevant_content.append((current_url, text))
                char_count += line_chars

    # Générer une réponse concise
    if not relevant_content:
        response = f"No relevant information found for prompt: {prompt}\nTry a more specific URL or broader keywords."
        return response[:max_chars]

    response = f"# Relevant Information for: {prompt}\n\n"
    char_count = len(response)
    for url, text in relevant_content:
        line = f"From {url}:\n- {text}\n"
        if char_count + len(line) > max_chars:
            break
        response += line
        char_count += len(line)

    return response[:max_chars]

def main():
    base_url = input("Enter the base URL to scrape: ").strip()
    if not base_url:
        print("Base URL required.")
        return

    prompt = input("Enter your query: ").strip()
    if not prompt:
        print("Prompt required.")
        return

    # Détecter la langue (simplifié)
    language = 'french' if 'wikipedia.org/wiki' in base_url else 'english'
    keywords = extract_keywords(prompt, language)
    tags_to_extract = ['title', 'h1', 'h2', 'h3', 'p', 'div', 'li']

    results = crawl_links(base_url, keywords, tags_to_extract)

    # Sauvegarder le contenu brut
    md_file = 'output.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Scraped results for: {prompt}\n\n")
        for url, texts in results:
            f.write(f"\n--- {url} ---\n")
            for line in texts:
                f.write(f"- {line}\n")

    print("✅ Done! Scraped content saved to output.md.")

    # Filtrer et générer la réponse pertinente
    filtered_response = filter_relevant_content(md_file, keywords, prompt)
    with open('filtered_output.md', 'w', encoding='utf-8') as f:
        f.write(filtered_response)
    print("✅ Filtered response saved to filtered_output.md.")
    print(f"\nFiltered Response Preview (length: {len(filtered_response)} chars):")
    print(filtered_response)

if __name__ == "__main__":
    main()