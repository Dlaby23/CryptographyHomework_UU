"""
Fetch multiple Czech texts for enhanced corpus.
"""

import requests
import re
import time
import json
from substitution_cipher import SubstitutionCipher


def fetch_wikisource_full_text(base_page):
    """Fetch complete text including all chapters/subpages."""
    base_url = "https://cs.wikisource.org/w/api.php"
    
    # First get the main page to find all subpages
    params = {
        'action': 'parse',
        'format': 'json',
        'prop': 'text|links',
        'page': base_page
    }
    
    all_text = []
    processed_pages = set()
    
    def fetch_page(page_title):
        if page_title in processed_pages:
            return ""
        processed_pages.add(page_title)
        
        params = {
            'action': 'parse',
            'format': 'json',
            'prop': 'text',
            'page': page_title
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if 'parse' in data:
                html = data['parse']['text']['*']
                # Extract text
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'&[^;]+;', ' ', text)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
        except:
            pass
        return ""
    
    # Get main page
    main_text = fetch_page(base_page)
    all_text.append(main_text)
    
    # Look for chapter links
    try:
        response = requests.get(base_url, params={'action': 'parse', 'format': 'json', 'prop': 'links', 'page': base_page})
        data = response.json()
        
        if 'parse' in data and 'links' in data['parse']:
            links = data['parse']['links']
            for link in links:
                if '*' in link:
                    link_title = link['*']
                    # Check if it's a subpage (chapter)
                    if base_page in link_title or link_title.startswith(base_page + '/'):
                        print(f"    Fetching subpage: {link_title}")
                        sub_text = fetch_page(link_title)
                        if sub_text:
                            all_text.append(sub_text)
                        time.sleep(0.5)
    except:
        pass
    
    return ' '.join(all_text)


def fetch_all_czech_texts():
    """Fetch all specified Czech texts."""
    
    sources = [
        ("Krakatit", "Karel Čapek - Krakatit"),
        ("Osudy_dobrého_vojáka_Švejka_za_světové_války", "Jaroslav Hašek - Švejk"),
        ("F._L._Věk", "Alois Jirásek - F. L. Věk"),
        ("Babička", "Božena Němcová - Babička"),
        ("Mezi_proudy", "Alois Jirásek - Mezi proudy"),
        ("Povídky_malostranské", "Jan Neruda - Povídky malostranské"),
        ("Staré_pověsti_české", "Alois Jirásek - Staré pověsti české"),
        ("Nový_epochální_výlet_pana_Broučka,_tentokráte_do_XV._století", "Svatopluk Čech - Pan Brouček")
    ]
    
    cipher = SubstitutionCipher()
    all_texts = {}
    
    print("Fetching Czech texts for enhanced corpus...")
    
    for page_name, description in sources:
        print(f"\nFetching: {description}")
        
        try:
            text = fetch_wikisource_full_text(page_name)
            
            if text:
                processed = cipher.preprocess_text(text)
                if len(processed) > 5000:
                    all_texts[page_name] = {
                        'description': description,
                        'raw_length': len(text),
                        'processed_length': len(processed),
                        'text': processed
                    }
                    print(f"  ✓ Success: {len(processed):,} characters")
                else:
                    print(f"  ✗ Too short: {len(processed)} characters")
            else:
                print(f"  ✗ Failed to retrieve")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        time.sleep(1)
    
    # Save individual texts
    with open('czech_texts_metadata.json', 'w', encoding='utf-8') as f:
        metadata = {k: {**v, 'text': v['text'][:100] + '...'} for k, v in all_texts.items()}
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Combine all texts
    combined = '_'.join([data['text'] for data in all_texts.values()])
    
    # Save combined corpus
    with open('czech_corpus_enhanced.txt', 'w', encoding='utf-8') as f:
        f.write(combined)
    
    print(f"\n✓ Enhanced corpus created!")
    print(f"  Total texts: {len(all_texts)}")
    print(f"  Total size: {len(combined):,} characters")
    
    return combined, all_texts


if __name__ == "__main__":
    corpus, texts_data = fetch_all_czech_texts()