import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def extract_keywords(prompt, language='english'):
    words = word_tokenize(prompt.lower())
    stop_words = set(stopwords.words(language))
    keywords = [w for w in words if w.isalnum() and w not in stop_words]
    if 'dark' in keywords:
        keywords += (['shadow','dim','gloomy'] if language=='english' else ['sombre','noir','obscur'])
    return keywords

def fetch_soup(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'lxml')
    except:
        return None

def extract_text(soup, tags):
    out = []
    for t in tags:
        for el in soup.find_all(t):
            txt = el.get_text(strip=True)
            if txt:
                out.append(txt)
    return out

def crawl_and_collect(base_url, prompt, max_pages=5):
    language = 'french' if 'wikipedia.org/wiki' in base_url else 'english'
    keywords = extract_keywords(prompt, language)
    tags = ['title','h1','h2','h3','p','li','div']

    parsed_base = urlparse(base_url).netloc
    to_visit = {base_url}
    visited = set()
    pages = []
    while to_visit and len(visited)<max_pages:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        soup = fetch_soup(url)
        if not soup:
            continue
        texts = extract_text(soup, tags)
        pages.append((url, texts))
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            pl = urlparse(href).netloc
            txt = a.get_text(strip=True).lower()
            if pl==parsed_base and any(k in href.lower() or k in txt for k in keywords):
                if href not in visited:
                    to_visit.add(href)
    return pages

def filter_relevant(pages, prompt, max_chars=4000, min_len=15):
    irrelevant = ['sommaire','voir aussi','références','modifier','wikidata']
    keywords = [w.lower() for w in word_tokenize(prompt)]
    out = []
    count = 0
    for url, texts in pages:
        for t in texts:
            tl = t.strip()
            if len(tl)<min_len:
                continue
            if any(r in tl.lower() for r in irrelevant):
                continue
            if any(k in tl.lower() for k in keywords):
                entry = f"From {url}:\n• {tl}\n"
                if count + len(entry)>max_chars:
                    return out
                out.append(entry)
                count += len(entry)
    return out
