"""
Fetch multiple Czech texts from various sources for better statistical analysis.
"""

import requests
import re
from substitution_cipher import SubstitutionCipher
import time


def fetch_wikisource_text(page_title):
    """Fetch a text from Czech Wikisource."""
    base_url = "https://cs.wikisource.org/w/api.php"
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
        return ""
    
    return ""


def fetch_multiple_czech_texts():
    """Fetch various Czech texts to create comprehensive corpus."""
    
    cipher = SubstitutionCipher()
    texts = []
    
    # List of diverse Czech texts on Wikisource
    sources = [
        # Classic literature
        ("RUR", "Karel Čapek - R.U.R."),
        ("Babička", "Božena Němcová - Babička"),
        ("Máj", "Karel Hynek Mácha - Máj"),
        
        # Different authors and styles
        ("Povídky_malostranské", "Jan Neruda - Povídky"),
        ("Kytice", "Karel Jaromír Erben - Kytice"),
        ("Osudy_dobrého_vojáka_Švejka_za_světové_války", "Jaroslav Hašek - Švejk"),
        
        # Non-fiction
        ("Dějiny_národu_českého_v_Čechách_a_v_Moravě", "František Palacký - Dějiny"),
        
        # Modern texts
        ("Válka_s_mloky", "Karel Čapek - Válka s mloky"),
    ]
    
    print("Fetching diverse Czech texts...")
    
    for page, description in sources:
        print(f"\nFetching: {description}")
        
        try:
            # For multi-part works, try to get the main page
            text = fetch_wikisource_text(page)
            
            if not text:
                # Try with different formatting
                text = fetch_wikisource_text(page.replace('_', ' '))
            
            if text:
                processed = cipher.preprocess_text(text)
                if len(processed) > 10000:  # Only use substantial texts
                    texts.append(processed)
                    print(f"  ✓ Retrieved {len(processed):,} characters")
                else:
                    print(f"  ✗ Text too short ({len(processed)} chars)")
            else:
                print(f"  ✗ Failed to retrieve")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        time.sleep(1)  # Be polite to the server
    
    # Combine all texts
    combined_text = '_'.join(texts)
    
    return combined_text, texts


def fetch_czech_wikipedia_sample():
    """Fetch a sample of Czech Wikipedia for modern language."""
    
    print("\nFetching Czech Wikipedia sample...")
    
    # Get random articles from Czech Wikipedia
    url = "https://cs.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'random',
        'rnlimit': 10,
        'rnnamespace': 0
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        articles = data['query']['random']
        wiki_texts = []
        
        cipher = SubstitutionCipher()
        
        for article in articles[:5]:  # Get 5 random articles
            page_params = {
                'action': 'query',
                'format': 'json',
                'titles': article['title'],
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True
            }
            
            response = requests.get(url, params=page_params)
            page_data = response.json()
            
            pages = page_data['query']['pages']
            for page_id, page_info in pages.items():
                if 'extract' in page_info:
                    text = cipher.preprocess_text(page_info['extract'])
                    if len(text) > 500:
                        wiki_texts.append(text)
                        print(f"  ✓ {article['title']}: {len(text)} chars")
            
            time.sleep(0.5)
        
        return '_'.join(wiki_texts)
        
    except Exception as e:
        print(f"Wikipedia fetch error: {e}")
        return ""


def create_comprehensive_corpus():
    """Create a comprehensive Czech corpus from multiple sources."""
    
    print("Building comprehensive Czech corpus...")
    
    # 1. Get Krakatit (original)
    print("\n1. Loading Krakatit...")
    try:
        with open('krakatit_processed.txt', 'r') as f:
            krakatit = f.read()
        print(f"   Krakatit: {len(krakatit):,} characters")
    except:
        krakatit = ""
        print("   Krakatit: Not found")
    
    # 2. Get other literary texts
    print("\n2. Fetching additional literary texts...")
    literary_texts, individual_texts = fetch_multiple_czech_texts()
    
    # 3. Get modern Czech from Wikipedia
    print("\n3. Fetching modern Czech (Wikipedia)...")
    wiki_text = fetch_czech_wikipedia_sample()
    
    # Combine all sources
    all_texts = [krakatit] + individual_texts
    if wiki_text:
        all_texts.append(wiki_text)
    
    combined = '_'.join(filter(None, all_texts))
    
    # Save the corpus
    with open('czech_corpus_comprehensive.txt', 'w', encoding='utf-8') as f:
        f.write(combined)
    
    print(f"\n✓ Comprehensive corpus created!")
    print(f"  Total size: {len(combined):,} characters")
    print(f"  Sources: {len(all_texts)} different texts")
    
    # Save metadata
    metadata = {
        'total_chars': len(combined),
        'num_sources': len(all_texts),
        'source_lengths': [len(t) for t in all_texts if t]
    }
    
    import json
    with open('corpus_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return combined


if __name__ == "__main__":
    corpus = create_comprehensive_corpus()
    
    # Create new bigram matrix from comprehensive corpus
    from create_bigram_matrix import create_and_save_bigram_matrix
    print("\nCreating improved bigram matrix from comprehensive corpus...")
    
    # Save as different file to compare
    import numpy as np
    from substitution_cipher import BigramAnalysis
    import pickle
    
    analyzer = BigramAnalysis()
    bigram_matrix = analyzer.create_bigram_matrix(corpus)
    
    np.save('czech_bigram_matrix_comprehensive.npy', bigram_matrix)
    
    with open('czech_bigram_data_comprehensive.pkl', 'wb') as f:
        pickle.dump({
            'matrix': bigram_matrix,
            'alphabet': analyzer.alphabet,
            'source_text_length': len(corpus),
            'num_sources': len([t for t in corpus.split('_') if len(t) > 10000])
        }, f)
    
    print("✓ Comprehensive bigram matrix saved!")