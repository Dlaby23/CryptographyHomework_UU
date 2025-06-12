"""
Skript pro stažení textu Krakatit z Wikisource.
"""

import requests
import re
from substitution_cipher import SubstitutionCipher


def fetch_krakatit():
    """Stáhne text knihy Krakatit z Wikisource."""
    url = "https://cs.wikisource.org/wiki/Krakatit"
    
    print("Stahuji Krakatit z Wikisource...")
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Chyba při stahování: {response.status_code}")
    
    # Extrakce textu z HTML
    html = response.text
    
    # Odstranění HTML tagů a získání čistého textu
    # Hledáme text mezi značkami mw-parser-output
    start = html.find('<div class="mw-parser-output">')
    end = html.find('</div><!-- /mw-parser-output -->')
    
    if start == -1 or end == -1:
        raise Exception("Nepodařilo se najít obsah textu")
    
    content = html[start:end]
    
    # Odstranění HTML tagů
    content = re.sub(r'<[^>]+>', ' ', content)
    
    # Odstranění entit HTML
    content = re.sub(r'&[^;]+;', ' ', content)
    
    # Odstranění nadbytečných mezer
    content = re.sub(r'\s+', ' ', content)
    
    return content.strip()


def fetch_full_krakatit():
    """Stáhne kompletní text Krakatitu včetně všech kapitol."""
    base_url = "https://cs.wikisource.org/w/api.php"
    
    # Parametry pro API
    params = {
        'action': 'parse',
        'format': 'json',
        'prop': 'text',
        'page': 'Krakatit'
    }
    
    print("Stahuji seznam kapitol...")
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'parse' not in data:
        raise Exception("Chyba při získávání dat z API")
    
    html = data['parse']['text']['*']
    
    # Najdi všechny odkazy na kapitoly
    chapter_links = re.findall(r'href="/wiki/(Krakatit/[^"]+)"', html)
    chapter_links = list(set(chapter_links))  # Odstranění duplikátů
    
    print(f"Nalezeno {len(chapter_links)} kapitol")
    
    full_text = []
    cipher = SubstitutionCipher()
    
    # Stáhni každou kapitolu
    for i, chapter in enumerate(sorted(chapter_links), 1):
        print(f"Stahuji kapitolu {i}/{len(chapter_links)}: {chapter}")
        
        params['page'] = chapter
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'parse' in data:
            chapter_html = data['parse']['text']['*']
            # Extrakce textu
            chapter_text = re.sub(r'<[^>]+>', ' ', chapter_html)
            chapter_text = re.sub(r'&[^;]+;', ' ', chapter_text)
            chapter_text = re.sub(r'\s+', ' ', chapter_text)
            
            # Předpřiprav text
            processed = cipher.preprocess_text(chapter_text)
            if processed:
                full_text.append(processed)
    
    return '_'.join(full_text)


if __name__ == "__main__":
    try:
        # Stáhni text
        text = fetch_full_krakatit()
        
        # Ulož originální text
        with open('/Users/vaclavdlabac/Desktop/Cryptography Homework/krakatit_processed.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Text úspěšně stažen a zpracován!")
        print(f"Délka textu: {len(text)} znaků")
        print(f"Prvních 200 znaků: {text[:200]}")
        
    except Exception as e:
        print(f"Chyba: {e}")