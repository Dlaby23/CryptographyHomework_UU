"""
Skript pro stažení textu Krakatit z Wikisource.
"""

import requests
import re
from substitution_cipher import SubstitutionCipher
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_krakatit_from_wikisource():
    """Stáhne kompletní text Krakatitu včetně všech kapitol z Wikisource. Link lze použít jiný"""
    base_url = "https://cs.wikisource.org/w/api.php" 
    
    # Nastavení session s retry logikou jen pro spolehlivější stahovaní kontentu z internetu
    session = requests.Session()
    retry = Retry(
        total=5,
        read=5,
        connect=5,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Parametry pro API
    params = {
        'action': 'parse',
        'format': 'json',
        'prop': 'text',
        'page': 'Krakatit'
    }
    
    print("Stahuji seznam kapitol...")
    response = session.get(base_url, params=params, timeout=30)
    data = response.json()
    
    if 'parse' not in data:
        raise Exception("Chyba při získávání dat z API")
    
    html = data['parse']['text']['*']
    
    # Najdi všechny odkazy na kapitoly
    chapter_links = re.findall(r'href="/wiki/(Krakatit/[^"]+)"', html)
    chapter_links = list(set(chapter_links))  # Odstranění dupu
    
    print(f"Nalezeno {len(chapter_links)} kapitol")
    
    full_text = []
    cipher = SubstitutionCipher()
    
    # Stahuje každou kapitolu
    for i, chapter in enumerate(sorted(chapter_links), 1):
        print(f"Stahuji kapitolu {i}/{len(chapter_links)}: {chapter}")
        
        params['page'] = chapter
        
        # Opakování v případě nejakého problému
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = session.get(base_url, params=params, timeout=30)
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
                break  # Úspěch, pokračuj na další kapitolu
                
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"  Pokus {attempt + 1} selhal, zkouším znovu...")
                    time.sleep(2)  # Nechci dostat ip ban a přetěžovat server 
                else:
                    print(f"  Nelze stáhnout kapitolu {chapter}: {e}")
                    # Pokračuj s dalšími kapitolami i když jedna selže
    
    return '_'.join(full_text)

def main():
    """Hlavní funkce - stáhne text z internetu."""
    try:
        # Vytvoř adresář pro data
        os.makedirs('data', exist_ok=True)
        
        # Stáhni text z Wikisource
        print("Stahuji text Krakatit z Wikisource...")
        print("(Vyžaduje internetové připojení)")
        text = fetch_krakatit_from_wikisource()
        
        if len(text) < 100000:
            raise Exception("Stažený text je příliš krátký. Zkontrolujte internetové připojení.")
        
        # Ulož text
        output_path = 'data/krakatit_processed.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\nText úspěšně stažen a uložen!")
        print(f"Cesta: {output_path}")
        print(f"Délka textu: {len(text):,} znaků")
        
    except requests.exceptions.ConnectionError:
        print("CHYBA: Není dostupné internetové připojení!")
        print("Tento skript vyžaduje připojení k internetu pro stažení textu z Wikisource.")
        exit(1)
    except Exception as e:
        print(f"CHYBA: {e}")
        exit(1)

if __name__ == "__main__":
    main()